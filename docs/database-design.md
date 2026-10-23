# 数据库详细设计：雾桌在线虚拟桌游平台

> 文档版本：v0.1（详细设计草案）  
> 状态：用于课程设计讨论，尚非生产数据库迁移脚本。  
> 依据：仓库中的 raw/要求.txt、docs/plan.md、docs/knowledge-map.md 与 docs/system-design.md。课程理论的最终术语核对仍以 raw/Introduction to Distributed System-by JieSong NEU.pdf 为准。

## 1. 设计目标与边界

本设计把 PostgreSQL 作为房间权威状态、事件记录和操作去重的持久化来源。Redis 只承担在线状态、路由缓存和低延迟通知，不保存唯一的权威事实。地图图片等静态文件放在对象存储，数据库只保存资源键和元数据。

数据库需要支持：

1. 管理用户、房间、成员角色、邀请链接、地图、角色标记和战争迷雾。
2. 为同一房间的成功状态变更分配单调递增的 room sequence。
3. 在同一事务中提交权威状态、事件日志和操作去重结果。
4. 在客户端重试、服务重启和消息通知丢失时恢复正确状态。
5. 为每个房间记录当前协调者实例和单调递增的 epoch，拒绝旧协调者的过期写入。

本设计不要求用户数据、房间数据和所有实时数据都采用相同的一致性保证。在线状态和光标等瞬时信息允许短暂滞后；标记位置、回合状态和掷骰结果则必须遵守权威提交规则。

## 2. 实体关系与数据分层

~~~mermaid
erDiagram
    USER_ACCOUNT ||--o{ ROOM : owns
    USER_ACCOUNT ||--o{ ROOM_MEMBER : joins
    ROOM ||--o{ ROOM_MEMBER : contains
    ROOM ||--o{ ROOM_INVITE : issues
    ROOM ||--o{ GAME_MAP : contains
    GAME_MAP ||--o{ TOKEN : contains
    GAME_MAP ||--o{ FOG_REGION : defines
    ROOM ||--o{ ROOM_EVENT : records
    ROOM ||--o{ ROOM_OPERATION : deduplicates
    ROOM ||--o{ ROOM_SNAPSHOT : snapshots
    ROOM ||--|| ROOM_LEASE : coordinates

    USER_ACCOUNT {
      uuid user_id PK
      varchar display_name
      timestamptz created_at
    }
    ROOM {
      uuid room_id PK
      uuid owner_user_id FK
      varchar title
      varchar status
      bigint current_seq
    }
    ROOM_MEMBER {
      uuid room_id PK,FK
      uuid user_id PK,FK
      varchar member_role
      varchar member_status
    }
    ROOM_INVITE {
      uuid invite_id PK
      uuid room_id FK
      bytea code_hash UK
      timestamptz expires_at
    }
    GAME_MAP {
      uuid map_id PK
      uuid room_id FK
      varchar asset_key
      bigint version
    }
    TOKEN {
      uuid token_id PK
      uuid map_id FK
      uuid owner_user_id FK
      numeric x
      numeric y
      bigint version
    }
    FOG_REGION {
      uuid region_id PK
      uuid map_id FK
      jsonb geometry_json
      varchar visibility_mode
    }
    ROOM_EVENT {
      uuid room_id PK,FK
      bigint sequence PK
      uuid event_id UK
      uuid operation_id
      jsonb payload
    }
    ROOM_OPERATION {
      uuid room_id PK,FK
      uuid operation_id PK
      bytea request_hash
      varchar status
      bigint result_sequence
    }
    ROOM_SNAPSHOT {
      uuid room_id PK,FK
      bigint sequence PK
      int schema_version
      jsonb state_payload
    }
    ROOM_LEASE {
      uuid room_id PK,FK
      varchar owner_instance
      bigint epoch
      timestamptz lease_until
    }
~~~

**图 1：核心实体关系图。** 该图用于说明逻辑关系；具体字段约束以本文件后面的表结构为准。用户只能获取服务端根据其房间角色和可见范围生成的数据投影，不能直接下载包含完整隐藏信息的事件载荷或快照。

### 2.1 数据职责分层

| 数据层 | 代表表/系统 | 职责 |
|---|---|---|
| 业务实体 | user_account、room、room_member、room_invite | 用户身份、房间生命周期、成员和加入权限 |
| 场景状态 | game_map、token、fog_region | 地图元数据、标记位置、迷雾与可见性 |
| 可靠操作记录 | room_operation、room_event | 操作去重、已提交变更、房间内事件顺序 |
| 恢复数据 | room_snapshot | 在某一事件序号上的完整权威状态 |
| 协调状态 | room_lease | 房间协调者归属、租约期限与 fencing epoch |
| 辅助数据 | Redis、对象存储 | 在线状态、路由缓存、通知与地图文件 |

## 3. 核心表结构

以下 SQL 是便于讲解和后续实现的 PostgreSQL 结构草案。正式实现时还需要补充迁移脚本、权限配置、备份策略与数据保留周期。

### 3.1 用户、房间与成员

~~~sql
CREATE TABLE user_account (
    user_id UUID PRIMARY KEY,
    display_name VARCHAR(40) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE room (
    room_id UUID PRIMARY KEY,
    owner_user_id UUID NOT NULL REFERENCES user_account(user_id),
    title VARCHAR(100) NOT NULL,
    status VARCHAR(16) NOT NULL
        CHECK (status IN ('OPEN', 'CLOSED', 'ARCHIVED')),
    current_seq BIGINT NOT NULL DEFAULT 0 CHECK (current_seq >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE room_member (
    room_id UUID NOT NULL REFERENCES room(room_id),
    user_id UUID NOT NULL REFERENCES user_account(user_id),
    member_role VARCHAR(16) NOT NULL
        CHECK (member_role IN ('HOST', 'PLAYER', 'OBSERVER')),
    member_status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE'
        CHECK (member_status IN ('ACTIVE', 'LEFT', 'KICKED')),
    joined_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    left_at TIMESTAMPTZ,
    PRIMARY KEY (room_id, user_id)
);

CREATE INDEX idx_room_member_user_active
    ON room_member(user_id, room_id)
    WHERE member_status = 'ACTIVE';
~~~

字段解释：

- room.current_seq 是房间已提交事件的最新序号，创建时为 0；它不是时间戳，也不是跨房间的全局序号。
- room_member 的复合主键防止同一用户在同一房间被重复登记。
- 创建房间应在同一个业务事务中创建 room 记录，并将创建者登记为 HOST；数据库外键不能单独保证 owner_user_id 必然对应一个 HOST 成员，因此还需要应用层不变量检查。
- 用户离开房间时优先更新成员状态，不应随意删除历史事件引用到的用户记录。

### 3.2 邀请码

~~~sql
CREATE TABLE room_invite (
    invite_id UUID PRIMARY KEY,
    room_id UUID NOT NULL REFERENCES room(room_id),
    created_by UUID NOT NULL REFERENCES user_account(user_id),
    code_hash BYTEA NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ,
    max_uses INTEGER CHECK (max_uses IS NULL OR max_uses > 0),
    use_count INTEGER NOT NULL DEFAULT 0 CHECK (use_count >= 0),
    revoked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
~~~

邀请规则：

- 服务端生成随机且难以猜测的邀请码；数据库只保存邀请码的哈希，不保存可直接使用的明文。
- 加入房间时检查邀请码是否存在、是否过期、是否撤销、使用次数是否超限，并检查房间是否允许加入。
- 邀请码不是身份认证凭据的替代品；加入成功后仍要建立 room_member 成员关系。
- 如果课程实现只需要固定房间邀请码，也可以暂时简化邀请表，但应保留过期和撤销的设计扩展点。

### 3.3 地图、标记与战争迷雾

~~~sql
CREATE TABLE game_map (
    map_id UUID PRIMARY KEY,
    room_id UUID NOT NULL REFERENCES room(room_id),
    name VARCHAR(100) NOT NULL,
    asset_key TEXT,
    width INTEGER NOT NULL CHECK (width > 0),
    height INTEGER NOT NULL CHECK (height > 0),
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    version BIGINT NOT NULL DEFAULT 1 CHECK (version > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_game_map_room
    ON game_map(room_id, is_active);

CREATE TABLE token (
    token_id UUID PRIMARY KEY,
    map_id UUID NOT NULL REFERENCES game_map(map_id),
    owner_user_id UUID REFERENCES user_account(user_id),
    label VARCHAR(80),
    x NUMERIC(10, 2) NOT NULL,
    y NUMERIC(10, 2) NOT NULL,
    rotation NUMERIC(6, 2) NOT NULL DEFAULT 0,
    version BIGINT NOT NULL DEFAULT 1 CHECK (version > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_token_map ON token(map_id);

CREATE TABLE fog_region (
    region_id UUID PRIMARY KEY,
    map_id UUID NOT NULL REFERENCES game_map(map_id),
    geometry_json JSONB NOT NULL,
    visibility_mode VARCHAR(24) NOT NULL
        CHECK (visibility_mode IN (
            'HIDDEN_FOR_PLAYERS',
            'VISIBLE_TO_ALL',
            'VISIBLE_TO_USER'
        )),
    visible_to_user_id UUID REFERENCES user_account(user_id),
    version BIGINT NOT NULL DEFAULT 1 CHECK (version > 0),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (
        (visibility_mode = 'VISIBLE_TO_USER' AND visible_to_user_id IS NOT NULL)
        OR
        (visibility_mode <> 'VISIBLE_TO_USER' AND visible_to_user_id IS NULL)
    )
);

CREATE INDEX idx_fog_region_map ON fog_region(map_id);
~~~

字段与规则：

- asset_key 是对象存储中的资源键，不是对客户端公开的任意文件系统路径。
- token 的 x、y 表示地图坐标，允许小数以支持自由摆放；如果最终决定只支持网格移动，可以改成整数网格坐标。
- token.version 和 game_map.version 是对象版本，用于检查客户端是否基于过期对象状态发起修改。
- room.current_seq 则表示房间事件全序。对象版本和房间事件序号是两个不同概念，不能混用。
- geometry_json 存储迷雾区域的几何描述；服务端需要校验其结构与地图边界，客户端不能上传任意 JSON 后就直接广播。
- fog_region 的可见性模式是一个受控的简化模型。如果后续要求支持更复杂的个人视野或多层遮罩，应先补充业务规则再扩展结构。

## 4. 操作幂等、事件日志与快照

### 4.1 房间事件表

~~~sql
CREATE TABLE room_event (
    room_id UUID NOT NULL REFERENCES room(room_id),
    sequence BIGINT NOT NULL CHECK (sequence > 0),
    event_id UUID NOT NULL UNIQUE,
    operation_id UUID NOT NULL,
    actor_user_id UUID REFERENCES user_account(user_id),
    event_type VARCHAR(48) NOT NULL,
    payload JSONB NOT NULL,
    publish_attempts INTEGER NOT NULL DEFAULT 0 CHECK (publish_attempts >= 0),
    next_attempt_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (room_id, sequence),
    UNIQUE (room_id, operation_id)
);

CREATE INDEX idx_room_event_pending_publish
    ON room_event(next_attempt_at, created_at)
    WHERE published_at IS NULL;
~~~

事件表的含义：

- sequence 只在同一个 room_id 范围内唯一并递增，组成房间内的权威事件顺序。
- 一个成功的客户端变更操作在本版设计中生成一个规范事件；如果一次操作会改变多个对象，应在同一个事件载荷中描述这些变化，客户端将其作为一个原子事件应用。
- payload 保存服务端内部的规范事件数据，可能包含隐藏区域或其他敏感状态；它不是可直接广播给所有玩家的公共消息。
- published_at 表示事件通知已被发布器成功提交到通知通道，不表示每个客户端都收到了消息。
- 事件发布器通过扫描 published_at 为空的记录完成重试。通知内容只需要携带 room_id 和 sequence 等定位信息；网关再读取事件并按接收者权限生成投影，避免 Redis 通知中泄漏完整事件载荷。
- 发布器可能在发布成功、更新 published_at 之前崩溃，从而重复发布通知。因此消费者必须按 room_id 和 sequence 去重，不能承诺网络消息恰好投递一次。

### 4.2 操作去重表

~~~sql
CREATE TABLE room_operation (
    room_id UUID NOT NULL REFERENCES room(room_id),
    operation_id UUID NOT NULL,
    actor_user_id UUID NOT NULL REFERENCES user_account(user_id),
    operation_type VARCHAR(48) NOT NULL,
    request_hash BYTEA NOT NULL,
    status VARCHAR(16) NOT NULL
        CHECK (status IN ('PROCESSING', 'SUCCEEDED', 'REJECTED')),
    result_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    result_sequence BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (room_id, operation_id),
    FOREIGN KEY (room_id, result_sequence)
        REFERENCES room_event(room_id, sequence)
);

CREATE INDEX idx_room_operation_created
    ON room_operation(created_at);
~~~

- operation_id 是客户端为一次逻辑操作生成的唯一标识；客户端超时重试时必须复用原 ID。
- request_hash 是规范化请求内容的哈希。如果同一个 operation_id 被用于不同的请求内容，服务端应拒绝并返回幂等键冲突，而不是把旧结果误当成新操作的结果。
- SUCCEEDED 表示权威状态已提交；REJECTED 表示该操作已被确定拒绝并记录结果。失败原因写入 result_payload。
- PROCESSING 仅作为同一数据库事务中的临时状态；正常情况下不应让一个长期未完成的 PROCESSING 记录独立提交。若实现选择异步操作状态机，则必须另行定义恢复与超时规则。
- result_sequence 指向成功操作产生的房间事件；被拒绝的操作没有对应事件，result_sequence 为 NULL。
- 去重记录的保留时间至少覆盖客户端可能重试的时间窗口。清理策略确定前，不应随意删除近期操作记录。

### 4.3 快照表

~~~sql
CREATE TABLE room_snapshot (
    room_id UUID NOT NULL REFERENCES room(room_id),
    sequence BIGINT NOT NULL CHECK (sequence >= 0),
    schema_version INTEGER NOT NULL CHECK (schema_version > 0),
    state_payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (room_id, sequence)
);
~~~

快照约定：

- sequence = S 表示该快照是应用完房间所有已提交事件至 S 后的完整权威状态；sequence = 0 表示房间初始状态。
- 快照只用于服务端恢复和生成授权后的客户端状态投影。普通玩家不能直接下载含完整隐藏信息的 state_payload。
- schema_version 用于识别快照数据结构版本，便于未来迁移。
- 生成快照时必须保证 state_payload 与 sequence 对应同一一致性视图，不能一边读取旧事件序号、一边读取较新的标记位置。
- 快照保留周期和事件日志保留周期待性能测试与重连需求确认后决定。

## 5. 房间协调者租约

~~~sql
CREATE TABLE room_lease (
    room_id UUID PRIMARY KEY REFERENCES room(room_id),
    owner_instance VARCHAR(100),
    epoch BIGINT NOT NULL DEFAULT 0 CHECK (epoch >= 0),
    lease_until TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
~~~

租约字段含义：

- owner_instance：当前房间协调者的逻辑实例 ID，不是玩家可见地址。
- epoch：单调递增的任期号，也可称 fencing token。每次协调者发生新的接管时递增。
- lease_until：租约失效时间，以数据库时间为准，避免仅依赖不同服务实例可能存在偏差的物理时钟。
- 房间创建时应同时创建对应的 room_lease 记录。

每次权威写事务都要在数据库事务内锁定并校验租约记录，检查 owner_instance、epoch 和 lease_until。不能只在服务启动时检查一次，也不能仅用 Redis 锁代替数据库中的权威写入校验。

租约到期后，新协调者在获取记录锁的基础上递增 epoch 并取得新租约。旧协调者恢复后，如果仍使用旧 epoch，就必须被数据库写入路径拒绝。新协调者在状态恢复完成之前，不应接受该房间的新写操作。

## 6. 核心事务与并发控制

### 6.1 操作处理事务

以移动角色标记为例，房间服务按以下步骤执行：

1. 验证用户身份与房间成员权限。
2. 开启数据库事务，并对对应 room 记录执行行级锁定，确保同一房间的权威变更按顺序进入提交路径。
3. 查询 room_operation 是否已有相同的 operation_id：
   - 若请求哈希相同，返回已记录的原结果，不重复执行。
   - 若请求哈希不同，返回幂等键冲突。
4. 锁定并校验 room_lease，确保当前实例与 epoch 匹配且租约有效。
5. 检查成员角色、标记所有权、地图边界和 expectedObjectVersion。
6. 若业务校验失败，记录 REJECTED 结果并提交该拒绝结果，不推进 room.current_seq。
7. 若校验成功，更新标记位置并将 token.version 加一；将 room.current_seq 加一，取得新 sequence。
8. 插入 room_event 记录该变更，更新 room_operation 为 SUCCEEDED 并保存 result_sequence。
9. 提交事务。只有提交成功后，该操作才算权威状态变更。
10. 提交后由发布器发布通知；若发布失败，后续扫描会重试。

~~~mermaid
sequenceDiagram
    autonumber
    participant C as 客户端
    participant R as 房间服务
    participant DB as PostgreSQL
    participant P as 事件发布器
    participant G as WebSocket网关

    C->>R: 操作 + operationId + expectedObjectVersion
    R->>DB: BEGIN；锁定 room 行
    R->>DB: 检查 operationId 与 requestHash
    R->>DB: 校验租约 epoch 与权限
    R->>DB: 更新对象版本、room.current_seq、事件和操作结果
    DB-->>R: COMMIT 成功
    R-->>C: 返回已提交的权威结果
    P->>DB: 扫描待发布事件
    P->>G: 发布 roomId + sequence 通知
    G->>DB: 读取事件并按接收者生成投影
    G-->>C: 推送授权后的事件
~~~

**图 2：移动操作事务与事件发布流程。** 事务提交和消息投递是两个阶段。数据库事务成功但推送失败时，状态仍然有效；客户端通过通知重试、事件补发或快照恢复来追上权威状态。

### 6.2 为什么同时需要对象版本和房间序号

- expectedObjectVersion 用来判断某个对象是否在客户端读取后被其他人修改。例如，两名玩家同时移动同一个 token，第二个旧版本请求应被拒绝或重新验证。
- room.current_seq 用来给本房间所有已提交事件分配全序。例如地图切换、标记移动和回合推进属于不同对象，也仍然需要可比较的事件顺序。
- 不同房间各自维护 sequence，不要求 room A 的事件序号与 room B 的序号比较大小。
- 客户端时间戳只可用于展示或辅助诊断，不能决定最终权威顺序。

### 6.3 数据库锁与分布式互斥的关系

本方案在 PostgreSQL 事务中锁定 room 行，作为房间权威写入的串行化点。它属于依托共享数据库的协调式设计，并不等同于 Lamport、Ricart–Agrawala 或 Token Ring 等分布式互斥算法。

这项选择的理由是：课程项目的主要目标是解释一致性和故障边界，而不是实现一套额外的分布式锁协议。报告仍应对课堂互斥算法作适用性比较；不采用它们不代表它们没有价值。

## 7. 状态恢复流程

~~~mermaid
flowchart TD
    A["新协调者申请接管房间"]
    B["锁定租约记录并递增 epoch"]
    C["阻止旧 epoch 的权威写入"]
    D["读取最新快照 sequence = S"]
    E["按序重放 S+1 到当前最新事件"]
    F{"事件序号连续且状态校验通过？"}
    G["恢复完成，开始接受新写操作"]
    H["报告恢复异常并停止写入"]

    A --> B --> C --> D --> E --> F
    F -- 是 --> G
    F -- 否 --> H
~~~

**图 3：房间协调者恢复流程。** 新协调者应先完成租约接管并隔离旧任期，再恢复状态；不能让旧协调者和新协调者同时对同一房间接受写入。

客户端断线重连与服务端故障恢复不同：

- 客户端重连：提供 lastSequence；若缺失事件仍在日志中，则按序补发，否则发送授权后的快照，再补发快照之后的事件。
- 服务端恢复：先加载最新快照和后续持久事件，恢复完整权威状态；确认租约与任期有效后才开放新写入。
- 两条流程都以持久化事件序号为依据，而不是相信客户端本地状态。

## 8. 索引、保留与安全规则

### 8.1 索引原则

| 查询场景 | 索引依据 | 原因 |
|---|---|---|
| 查询用户当前加入的房间 | room_member(user_id, room_id) 的 ACTIVE 部分索引 | 避免扫描全部房间成员 |
| 查询房间地图 | game_map(room_id, is_active) | 快速定位当前场景 |
| 查询地图上的标记 | token(map_id) | 按地图读取空间对象 |
| 查询地图迷雾区域 | fog_region(map_id) | 按地图加载可见性区域 |
| 按序恢复房间事件 | room_event(room_id, sequence) 主键 | 支持范围扫描和连续序号校验 |
| 扫描待发布事件 | room_event(next_attempt_at, created_at) 的未发布部分索引 | 减少重复扫描已发布事件 |
| 获取最新快照 | room_snapshot(room_id, sequence) 主键 | 可按房间与序号定位快照 |
| 幂等去重 | room_operation(room_id, operation_id) 主键 | 快速查找操作结果 |

索引不是越多越好。每个额外索引都会增加写入和存储成本；后续应根据实际查询和压力测试结果决定是否增加复合索引。

### 8.2 保留策略

- room_event 的保留范围必须足以支持最新快照之后的重放。删除旧事件前，应确认已有可用快照覆盖相应历史。
- room_operation 的保留范围必须覆盖客户端最大重试窗口；否则过期请求可能被误当作新操作再次执行。
- 快照应保留至少一个可验证的最新版本；是否额外保留历史快照由恢复需求和存储成本决定。
- 成员退出不意味着房间事件和操作记录可以立刻删除。
- 具体天数、快照间隔和最大事件补发量暂不指定，待设计目标与测试环境确定后再定。

### 8.3 安全规则

1. 所有修改操作必须经过服务端鉴权和对象级授权。
2. 隐藏地图区域和完整快照只允许服务端读取，网关必须生成按接收者过滤的投影。
3. 邀请码只存哈希；日志不记录明文邀请码、访问令牌或其他认证凭据。
4. 所有 JSONB 输入都必须做字段白名单、长度、类型和业务范围校验。
5. 数据库账号按职责授予最小权限；网关不应拥有直接修改权威状态的权限。
6. 对事件日志与快照的访问也要进行授权检查，不能因为它们是“内部数据”就忽略权限边界。

## 9. 替代方案与取舍

| 方案 | 优点 | 当前不作为主方案的原因 |
|---|---|---|
| PostgreSQL 事务 + 房间行锁 | 状态、序号、事件和幂等结果可在同一事务提交；容易解释和测试 | 高竞争单房间的吞吐受序列化点限制，需压测验证 |
| Redis 分布式锁作为唯一协调依据 | 获取锁速度快，部署常见 | 锁服务与业务状态事务分离；若没有 fencing 和写入端校验，旧持有者可能继续写入 |
| 客户端时间戳排序 | 实现直观 | 客户端时钟可能偏差，时间戳不能可靠代表提交顺序 |
| Lamport/向量时钟直接合并所有状态 | 适合表达因果关系或识别并发 | 当前房间已有权威协调者，增加复杂度但不改善核心业务需求 |
| Kafka 作为唯一事件源 | 适合高吞吐事件流与消费组场景 | 对当前课程设计范围过重；无论是否采用消息平台，权威状态与恢复边界仍需清楚 |
| CRDT/P2P 无中心合并 | 在部分离线协同场景中可提高本地可用性 | 本系统需要服务端执行权限、掷骰和回合规则；初版采用权威服务端排序更容易验证 |
| 2PC/3PC | 可讨论跨多个参与者的分布式提交 | 当前核心状态、事件与操作结果可放在同一个数据库事务中，不需要为此引入跨服务原子提交 |

## 10. 验收用例

| 编号 | 测试场景 | 预期结果 |
|---|---|---|
| DB-01 | 创建房间 | room、HOST 成员与 room_lease 初始化成功，或全部回滚 |
| DB-02 | 同一用户重复加入房间 | 不产生重复 room_member 记录 |
| DB-03 | 同一 operation_id、相同请求重试 | 返回原结果，不重复改变 token 位置或 room.current_seq |
| DB-04 | 同一 operation_id、不同请求内容 | 返回幂等键冲突，不覆盖原结果 |
| DB-05 | 两个客户端以同一 token.version 发起移动 | 至多一个基于旧版本成功；另一个需刷新或重新验证 |
| DB-06 | 权威状态更新后插入事件失败 | 整个事务回滚，不出现只有状态变化却没有事件记录的情况 |
| DB-07 | 事务提交后、通知发布前发布器崩溃 | 待发布事件仍在数据库中，发布器重启后可继续通知 |
| DB-08 | 通知重复发布 | 网关/客户端依据 room_id 与 sequence 去重，不重复应用事件 |
| DB-09 | 旧协调者使用旧 epoch 写入 | 数据库写入路径拒绝旧任期操作 |
| DB-10 | 普通玩家请求完整快照或隐藏区域 | 服务端拒绝，或只返回授权后的状态投影 |
| DB-11 | 客户端 lastSequence 早于日志保留范围 | 服务端返回授权快照与其后的事件，而不是伪造缺失事件 |
| DB-12 | 房间事件连续性检查失败 | 恢复过程停止开放写入并记录异常，避免在不完整状态上继续服务 |

## 11. 与课程 Chapter 1–8 的对应

| 课件章节 | 本设计对应内容 | 可用于报告的论证 |
|---|---|---|
| Chapter 1 导论 | 事务边界、ACID、网络不可靠假设 | 为什么权威状态与事件要原子提交 |
| Chapter 2 体系结构 | 数据职责分层、数据库权威源、缓存和通知分离 | 为什么不是所有组件都承担权威职责 |
| Chapter 3 进程 | 房间服务的串行化点、后台发布器 | 为什么不同房间可以并行、同房间状态写入需要协调 |
| Chapter 4 通信 | 事件发布、通知重试、客户端补发 | 为什么 WebSocket 通知不等于持久化或送达保证 |
| Chapter 5 命名 | UUID、room_id、map_id、operation_id、邀请码哈希 | 区分稳定标识、邀请凭据与网络地址 |
| Chapter 6 同步 | room.current_seq、对象版本、租约 epoch | 区分事件全序、对象并发检测与协调者任期 |
| Chapter 7 一致性与复制 | 事务、持久事件、快照、主备复制边界 | 定义房间权威状态和客户端可见状态的保证 |
| Chapter 8 容错 | 幂等、日志重放、快照恢复、fencing token | 说明进程崩溃、重复请求和旧协调者恢复时的行为 |

## 12. 尚待确认与下一步

以下内容目前仍是设计建议，不应写成教师硬性规定或已实现事实：

1. 房间人数、实时延迟与重连恢复目标，继续以 docs/questions.md 中的待确认项为准。
2. 地图资源是否需要用户上传；若需要，需补充上传授权、资源校验、文件大小限制和对象存储访问策略。
3. 具体的事件保留天数、快照间隔、数据库复制模式与备份恢复目标，需要结合课程范围和后续测试确定。
4. 表结构为概要详细设计草案；实现前仍需补充数据库迁移、角色权限、外键删除策略、备份/恢复操作和异常处理。
5. 下一阶段应定义 REST/WebSocket 消息协议，使 operationId、expectedObjectVersion、room sequence 和事件投影在接口、数据库和报告中保持一致。
