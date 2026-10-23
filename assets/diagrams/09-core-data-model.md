# 图 9：核心数据实体关系图

**用途：** 展示业务实体、房间事件日志、幂等操作记录、快照与协调者租约之间的主要关系。  
**建议报告位置：** 第 6 章“数据模型设计”。  
**状态：** 逻辑 ER 图；字段级定义以 docs/database-design.md 为准。

~~~mermaid
erDiagram
    USER_ACCOUNT ||--o{ ROOM : owns
    USER_ACCOUNT ||--o{ ROOM_MEMBER : joins
    ROOM ||--o{ ROOM_MEMBER : contains
    ROOM ||--o{ ROOM_INVITE : issues
    USER_ACCOUNT ||--o{ ROOM_INVITE : creates
    ROOM ||--o{ GAME_MAP : contains
    GAME_MAP ||--o{ TOKEN : contains
    USER_ACCOUNT ||--o{ TOKEN : controls
    GAME_MAP ||--o{ FOG_REGION : defines
    ROOM ||--o{ ROOM_EVENT : records
    ROOM ||--o{ ROOM_OPERATION : deduplicates
    ROOM ||--o{ ROOM_SNAPSHOT : snapshots
    ROOM ||--|| ROOM_LEASE : coordinates
    USER_ACCOUNT {
      uuid user_id PK
      varchar display_name
    }
    ROOM {
      uuid room_id PK
      uuid owner_user_id FK
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
      text asset_key
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
    }
    ROOM_OPERATION {
      uuid room_id PK,FK
      uuid operation_id PK
      varchar status
      bigint result_sequence
    }
    ROOM_SNAPSHOT {
      uuid room_id PK,FK
      bigint sequence PK
      int schema_version
    }
    ROOM_LEASE {
      uuid room_id PK,FK
      varchar owner_instance
      bigint epoch
      timestamptz lease_until
    }
~~~

**关键说明：** 该图只展示主要实体和关联，不替代完整 SQL。房间事件、操作去重与快照的准确约束以数据库详细设计为准。
