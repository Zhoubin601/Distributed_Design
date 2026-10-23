# 图 4：移动标记的权威提交时序图

**用途：** 说明一次协作操作从请求、校验、事务提交到实时通知的完整链路。  
**建议报告位置：** 第 4 章“通信机制”或第 7 章“一致性与复制”。  
**状态：** 与数据库详细设计的事务与事件发布模型对齐的草图。

~~~mermaid
sequenceDiagram
    autonumber
    participant C as 玩家客户端
    participant W as WebSocket 网关
    participant R as 房间服务
    participant D as PostgreSQL
    participant P as 事件发布器
    participant G as 房间成员网关
    C->>W: MOVE_TOKEN + operationId + expectedVersion
    W->>R: 转发已认证的操作意图
    R->>D: BEGIN；锁定房间权威记录
    R->>D: 检查 operationId、请求哈希、权限与租约 epoch
    R->>D: 校验对象版本并更新状态、sequence、事件与操作结果
    D-->>R: COMMIT 成功
    R-->>W: 返回已提交的权威结果
    P->>D: 扫描尚未发布的已提交事件
    P-->>G: 发布 roomId + sequence 通知
    G->>D: 读取事件并按接收者权限生成投影
    G-->>C: 推送授权后的 ROOM_EVENT
~~~

**关键说明：**
- 状态、事件和幂等结果必须在同一个数据库事务中提交。
- 数据库提交后即使通知暂时失败，事件仍可由发布器重试或由客户端重连补发。
- 通知可能重复；消费者以 roomId 与 sequence 去重。
- WebSocket 发送成功不是数据库提交的替代品，也不是所有客户端均已收到的证明。
