# 通信接口与实时消息协议：雾桌在线虚拟桌游平台

> 文档版本：v0.1（接口设计草案）  
> 状态：概要设计阶段，尚未实现或进行互操作测试。  
> 关联文档：[系统概要设计](./system-design.md)、[数据库详细设计](./database-design.md)、[课程知识点映射](./knowledge-map.md)。

## 1. 设计原则

本协议将房间管理类请求与实时协作消息分开：

- HTTPS/REST 用于创建房间、加入房间、读取房间配置和获取地图元数据等请求—应答操作。
- WebSocket 用于实时操作请求、操作结果通知和房间事件推送。
- PostgreSQL 事务决定权威状态是否提交；WebSocket 消息发送成功不等于数据库提交成功，客户端收到消息也不代表消息已持久化。
- 每次可重试的客户端写操作必须带稳定的 operationId；重试时复用原 ID。
- 数据库内部 room_event.sequence（内部 roomSequence）为完整房间事件流排序，但不直接作为客户端可见的连续序号。服务端按当前权限生成投影后，为该授权视图流分配连续的 deliverySequence。
- 任何面向客户端的事件，都必须先通过房间成员权限和可见性过滤。服务端内部规范事件不直接广播给所有玩家。

## 2. 逻辑接口总览

| 类别 | 方法/消息 | 用途 | 是否改变权威状态 |
|---|---|---|---|
| 房间管理 | POST /api/rooms | 创建房间与主持人关系 | 是 |
| 房间管理 | POST /api/rooms/{roomId}/join | 校验邀请码并加入房间 | 是 |
| 房间查询 | GET /api/rooms/{roomId} | 获取当前用户有权看到的房间信息 | 否 |
| 场景查询 | GET /api/rooms/{roomId}/maps | 获取有权查看的地图元数据 | 否 |
| 实时连接 | WebSocket /ws/rooms/{roomId} | 建立已认证的房间实时连接 | 否 |
| 实时写入 | MOVE_TOKEN、ROLL_DICE、SET_FOG 等 | 请求执行一个房间操作 | 经服务端校验和事务提交后才改变 |
| 恢复 | RESUME_FROM、事件补发或快照 | 恢复客户端事件进度 | 否 |
| 连接维护 | PING/PONG | 观察连接是否仍活跃 | 否 |

以上路径是建议的逻辑接口命名，正式实现时可按框架规范调整，但必须保持消息语义一致。

## 3. 统一消息封装

### 3.1 客户端请求

~~~json
{
  "messageType": "COMMAND",
  "roomId": "room-uuid",
  "operationId": "operation-uuid",
  "command": "MOVE_TOKEN",
  "expectedObjectVersion": 7,
  "payload": {
    "tokenId": "token-uuid",
    "x": 12.5,
    "y": 8
  }
}
~~~

字段含义：

| 字段 | 说明 |
|---|---|
| messageType | 消息类别；写操作请求为 COMMAND |
| roomId | 目标房间标识 |
| operationId | 本次逻辑操作的稳定唯一标识；重试时不能换新 ID |
| command | 服务端支持的操作类型，采用白名单 |
| expectedObjectVersion | 客户端读到的对象版本；对不依赖对象版本的命令可省略 |
| payload | 命令参数；必须按 command 类型校验字段、类型和取值范围 |

服务端不能把客户端提交的用户 ID、角色、房间序号或掷骰结果当作可信权威字段。身份来自已认证连接；操作权限来自服务端成员记录；room sequence 与随机结果由服务端生成。

### 3.2 服务端操作结果

~~~json
{
  "messageType": "COMMAND_RESULT",
  "roomId": "room-uuid",
  "operationId": "operation-uuid",
  "status": "SUCCEEDED",
  "eventId": "event-uuid",
  "result": {
    "tokenId": "token-uuid",
    "x": 12.5,
    "y": 8,
    "objectVersion": 8
  }
}
~~~

status 只表示本次操作的权威处理结果：

- SUCCEEDED：状态变更和事件记录已经在数据库事务中提交。
- REJECTED：操作被业务规则或权限规则确定拒绝，返回稳定错误码。
- RETRYABLE_ERROR：当前无法确定成功提交结果或依赖服务暂时不可用；客户端可以用同一 operationId 重试。
- CONFLICT：对象版本过期或幂等键内容冲突，需要客户端按错误码决定刷新或停止重试。

如果连接在提交后、结果返回前断开，客户端无法仅凭超时判断操作是否成功。它应以同一个 operationId 重试或查询操作结果；服务端若已记录结果，返回原结果而不再次执行。

### 3.3 房间事件

~~~json
{
  "messageType": "ROOM_EVENT",
  "roomId": "room-uuid",
  "deliverySequence": 42,
  "viewVersion": 3,
  "resumeCursor": "opaque-resume-cursor",
  "eventId": "event-uuid",
  "operationId": "operation-uuid",
  "eventType": "TOKEN_MOVED",
  "payload": {
    "tokenId": "token-uuid",
    "x": 12.5,
    "y": 8,
    "objectVersion": 8
  }
}
~~~

这是经过权限过滤后的客户端事件示例。真实发送给玩家的 payload 由服务端按用户权限生成；例如隐藏区域中的标记不能通过事件载荷、快照或错误消息泄露给未授权玩家。deliverySequence 只在当前 roomId + viewVersion 的授权视图流中连续递增；resumeCursor 是不透明游标，不能让客户端反推出被过滤的内部事件数量。内部 roomSequence 不发送给普通客户端。

客户端按以下规则处理：

1. viewVersion 与当前视图不一致：停止应用该流，重新鉴权并请求当前权限下的快照。
2. deliverySequence 小于或等于本地 lastDeliverySequence：视为重复或过期事件，忽略。
3. deliverySequence 等于 lastDeliverySequence + 1：验证事件后应用，并推进 lastDeliverySequence。
4. deliverySequence 大于 lastDeliverySequence + 1：当前授权视图流存在缺口，暂停后续依赖事件的应用，并使用最后确认的 resumeCursor 请求补发或快照。
5. 定期比较 SYNC_WATERMARK 中的 latestDeliverySequence 与本地进度，以发现“最后一条通知丢失、之后没有新事件”的情况。不能用内部 roomSequence 的跳号直接判断客户端丢消息。
6. 若事件无法通过结构或版本校验，不应静默跳过并继续声称状态完整；应重新同步并记录诊断信息。

## 4. REST 接口草案

### 4.1 创建房间

POST /api/rooms

请求：

~~~json
{
  "title": "Friday Session",
  "maxMembers": 8
}
~~~

成功响应（逻辑示例）：

~~~json
{
  "roomId": "room-uuid",
  "status": "OPEN",
  "memberRole": "HOST",
  "inviteCode": "one-time-display-value"
}
~~~

设计约束：

- 创建房间、创建主持人成员关系和初始化房间租约应具备事务性；任一步失败都不能留下半初始化房间。
- 明文邀请码仅在创建或轮换时展示一次；持久化时只保存哈希。
- maxMembers 的上限应由服务端配置约束，不能完全相信客户端提供的值。

### 4.2 加入房间

POST /api/rooms/{roomId}/join

请求：

~~~json
{
  "inviteCode": "user-entered-code"
}
~~~

服务端检查身份、邀请码哈希、过期/撤销状态、使用次数、房间状态和成员限制。成功后创建或恢复 room_member 记录，并返回经过权限过滤的房间摘要。

加入房间不是授权读取所有事件的通行证。之后每次读取地图、获取快照或接收事件时，仍需要检查当前成员角色和可见范围。

### 4.3 查询操作结果

建议提供 GET /api/rooms/{roomId}/operations/{operationId}，或让同一 operationId 的 WebSocket 重试直接返回结果。

响应状态需要区分：
- 已成功提交：返回 SUCCEEDED 与原 sequence/result。
- 已确定拒绝：返回 REJECTED 与稳定错误码。
- 仍在处理：仅在实现真正支持已提交的异步处理中间状态时返回。
- 未找到：不能自动断言原操作失败；需结合写入协议决定是否允许客户端用同一 ID 再提交。

## 5. 错误码与客户端动作

| 错误码 | 含义 | 客户端建议动作 |
|---|---|---|
| AUTH_REQUIRED | 连接或请求没有有效身份 | 重新认证后重试 |
| ROOM_NOT_FOUND | 房间不存在或当前用户不可访问 | 停止重试并显示不可访问 |
| ROOM_CLOSED | 房间已关闭 | 停止写操作 |
| PERMISSION_DENIED | 当前成员无权执行该命令 | 不自动重试 |
| INVALID_PAYLOAD | 消息格式或参数不合法 | 修正参数后再发起新操作 |
| OBJECT_VERSION_CONFLICT | 对象版本已变化 | 拉取最新对象并让用户确认或重新执行 |
| IDEMPOTENCY_KEY_REUSED | 同一 operationId 对应了不同请求内容 | 作为客户端协议错误处理，不能自动生成新 ID 重放旧意图 |
| RATE_LIMITED | 请求过于频繁 | 按 retryAfter 退避后重试；复用原 operationId |
| TEMPORARY_UNAVAILABLE | 数据库或依赖暂时不可用 | 使用指数退避；写操作保持原 operationId |
| RESYNC_REQUIRED | 事件序号存在缺口或本地状态无法验证 | 请求事件补发或快照 |
| COORDINATOR_EPOCH_STALE | 当前服务实例的租约任期已过期 | 由客户端重连/重新路由，不无限重复同一旧连接请求 |

错误响应不应泄露隐藏地图数据、内部 SQL、数据库凭据或其他用户的个人信息。

## 6. 断线重连协议

客户端为当前授权视图维护 `lastDeliverySequence` 与 `resumeCursor`。游标绑定 roomId、当前成员和 viewVersion；它是服务端签发的不透明恢复位置，不直接暴露内部 roomSequence。

~~~mermaid
sequenceDiagram
    autonumber
    participant C as 客户端
    participant G as WebSocket网关
    participant R as 房间服务
    participant D as PostgreSQL

    C->>G: 连接并认证
    C->>G: RESUME_FROM(roomId, resumeCursor, lastDeliverySequence, viewVersion)
    G->>R: 校验成员权限与当前 viewVersion
    R->>D: 从游标之后扫描持久事件至当前水位
    R->>R: 按当前权限过滤并分配连续 deliverySequence
    alt 游标有效且视图未变化
        R-->>G: 授权事件 + SYNC_COMPLETE
        G-->>C: 按序发送 ROOM_EVENT 与新 resumeCursor
    else 游标失效或权限视图变化
        R->>D: 读取一致性快照及其内部 roomSequence
        R-->>G: 当前权限下的快照投影 + 后续授权事件
        G-->>C: ROOM_SNAPSHOT + ROOM_EVENT + SYNC_COMPLETE
    end
    C-->>G: RESUME_ACK(lastDeliverySequence, viewVersion)
~~~

**图 1：重连恢复消息流程。** 快照必须在当前权限下重新生成或从安全的权限分区读取。若成员角色或可见范围变化，旧 viewVersion 对应的游标失效，客户端必须替换本地状态，不能把旧权限下的快照与新视图简单合并。

恢复完成时的 `SYNC_COMPLETE` 与周期性的 `SYNC_WATERMARK` 都应包含 latestDeliverySequence、resumeCursor 和 viewVersion。只有当客户端已连续应用到 latestDeliverySequence 时，才可将返回的游标保存为新的恢复起点；若服务端水位更高，应继续补发。

## 7. 实时连接与发布语义

### 7.1 连接管理

- WebSocket 建立时验证身份；每个房间连接都要验证成员权限。
- 连接中断后，服务端清理临时在线状态，但不能因此删除成员身份或权威房间数据。
- 心跳只用于判断连接是否可能失效，不用于证明对端一定崩溃。
- 网关扩缩容或重启后，客户端可重新连接其他网关，并按 roomId 重新解析房间协调者。

### 7.2 发布语义

本系统不声称网络消息“恰好投递一次”。合理目标是：

1. 权威状态、内部 roomSequence、事件记录和操作结果在一个数据库事务中提交。
2. 当前方案使用 room_event 的待发布字段重试通知；通知通道只负责提示网关检查新事件，不是客户端收齐事件的证明。
3. 网关从每个连接的 resumeCursor 扫描持久事件，按当前权限生成投影，并为该视图分配连续 deliverySequence。
4. 通知可能重复、延迟或丢失；按 eventId/内部 roomSequence 去重，客户端按 deliverySequence 检查授权视图流。
5. 心跳或周期性对账发送 SYNC_WATERMARK，确保最后一条通知丢失且之后没有新事件时，客户端仍能发现落后并触发补发。
6. 权限过滤在实时推送、补发和快照路径都执行；权限版本变化时使旧游标失效。

## 8. 安全与输入校验

- 所有连接使用安全传输；具体 TLS 终止位置由部署方案决定。
- 每条消息限制最大字节数、JSON 深度、字段数量和允许的命令类型。
- 移动标记时校验 token 所属地图/房间、坐标边界、所有权和对象版本。
- 掷骰子时只接受骰子规则和请求参数，不接受客户端提交的最终点数作为权威结果。
- 设置战争迷雾时校验几何结构、地图边界与操作者角色。
- 客户端提供的时间戳只作为辅助诊断字段；权威顺序由服务端 sequence 决定。
- 对创建房间、加入房间和高频写操作设置合理限流；限流拒绝必须返回可理解的错误语义。
- 事件 payload 与快照在服务端内部属于可能含有隐藏信息的资料；日志应避免记录完整私有载荷。

## 9. 课程知识点映射

| 课件章节 | 接口协议中的应用 |
|---|---|
| Chapter 1 导论 | 网络延迟、断线、重复消息和不确定失败的假设 |
| Chapter 2 体系结构 | REST 管理接口、WebSocket 实时层与持久化层分工 |
| Chapter 3 进程 | 网关与房间服务职责、重连后重新定位服务实例 |
| Chapter 4 通信 | 请求—应答、消息通信、发布订阅、确认、超时、重试与补发 |
| Chapter 5 命名 | roomId、operationId、eventId 与网络地址的区分 |
| Chapter 6 同步 | room sequence、对象版本、并发操作排序 |
| Chapter 7 一致性与复制 | 权威提交、客户端事件顺序、快照和读自身写的处理 |
| Chapter 8 容错 | 幂等重试、连接恢复、事件重放与协调者任期过期错误 |

## 10. 验收测试

| 编号 | 测试场景 | 预期结果 |
|---|---|---|
| API-01 | 同一操作成功提交但响应丢失，客户端使用原 ID 重试 | 返回原结果，不产生第二次副作用 |
| API-02 | operationId 相同但请求内容变化 | 返回 IDEMPOTENCY_KEY_REUSED |
| API-03 | 客户端收到 sequence=10 后直接收到 sequence=12 | 暂停依赖事件应用并请求 sequence=11 或快照 |
| API-04 | 用户被移除房间后重连 | 认证成功也不能恢复该房间的成员权限 |
| API-05 | 普通玩家尝试读取完整迷雾状态 | 服务端拒绝或只返回授权投影 |
| API-06 | 掷骰子请求被重复发送 | 返回同一已提交骰子结果，不重新掷骰 |
| API-07 | 通知重复投递 | 客户端不会重复应用相同 sequence |
| API-08 | 服务端数据库暂时不可用 | 不返回“已提交”结果；客户端可用原 operationId 重试 |
| API-09 | 客户端快照版本不兼容 | 服务端协商兼容版本或要求完整重同步，不静默合并 |
| API-10 | 旧协调者发送写请求 | 权威写入路径拒绝旧 epoch 的操作 |
| API-11 | 房间中出现玩家无权查看的隐藏事件 | 客户端可见 deliverySequence 仍连续；不泄露隐藏事件载荷或内部事件数量 |
| API-12 | 最后一条可见事件的通知丢失，之后没有新事件 | SYNC_WATERMARK/周期对账发现服务端 deliverySequence 更高，并补发缺失事件 |
| API-13 | 成员权限或战争迷雾可见范围发生变化 | 旧 viewVersion/cursor 失效；服务端发送当前权限下的新快照 |

## 11. 待实现决策

1. WebSocket 鉴权采用短期票据还是已有会话 Cookie，需结合实际登录方案确定。
2. 是否支持同一用户多个设备同时加入同一房间，以及它们的 lastSequence 如何分别维护。
3. 掷骰规则的表达格式与随机数生成策略需要在业务规则设计中进一步定义。
4. 地图上传、静态资源授权与文件限制取决于是否把用户上传纳入核心范围。
5. 当前建议用 room_event 的 published_at、publish_attempts 和 next_attempt_at 作为待发布重试队列；如未来改为独立 outbox 或专用消息队列，仍需保留持久事件、权限投影与幂等语义。
6. deliverySequence 的连接级状态维护、resumeCursor 的签发/校验与 viewVersion 变化时的重置规则，需在实现前定稿。
