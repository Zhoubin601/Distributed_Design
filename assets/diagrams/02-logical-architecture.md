# 图 2：系统逻辑架构图

**用途：** 解释请求如何进入系统、谁负责权威状态、持久化和事件推送如何分工。  
**建议报告位置：** 第 2 章“总体架构设计”。  
**状态：** 基于当前概要设计整理；需与最终接口和数据库文档同步。

~~~mermaid
flowchart TB
    subgraph CLIENT["浏览器客户端"]
        HOST["主持人客户端"]
        PLAYER["玩家客户端"]
    end
    subgraph ACCESS["接入层"]
        API["HTTPS / REST API"]
        WS["WebSocket 网关"]
    end
    subgraph APP["应用与协作层"]
        AUTH["身份与权限校验"]
        ROUTER["房间路由"]
        ROOM["房间服务集群<br/>房间内权威排序"]
        PUBLISHER["事件发布器 / Outbox 扫描"]
    end
    subgraph DATA["数据与基础设施"]
        PG[("PostgreSQL<br/>权威状态、操作记录、事件、快照、租约")]
        REDIS[("Redis<br/>在线状态、路由缓存、即时通知")]
        OBJECT[("对象存储<br/>地图与静态资源")]
    end
    HOST --> API
    PLAYER --> API
    HOST <--> WS
    PLAYER <--> WS
    API --> AUTH
    WS --> AUTH
    AUTH --> ROUTER
    ROUTER --> ROOM
    ROOM <--> PG
    ROOM <--> REDIS
    ROOM --> OBJECT
    PUBLISHER --> PG
    PUBLISHER --> REDIS
    REDIS -. "通知房间事件已可读取" .-> WS
    WS -->|"按接收者权限读取并投影事件"| PG
~~~

**关键边界：**
- PostgreSQL 是权威持久化来源；Redis 通知丢失不能导致权威事件丢失。
- 房间服务负责权限、规则、对象版本与房间事件序号的权威校验。
- 事件发布成功不代表每个客户端都已收到；客户端依靠序号补发或快照恢复。
- 网关不能把含有完整战争迷雾信息的内部事件无差别广播给所有玩家。
