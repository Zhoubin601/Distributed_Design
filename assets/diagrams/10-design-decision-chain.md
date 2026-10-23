# 图 10：从业务需求到分布式机制的设计链

**用途：** 把核心业务需求、关键机制与最终可观察行为连接起来，避免报告只堆砌技术名词。  
**建议报告位置：** 第 2 章结尾，或作为第 6–8 章的概览图。  
**状态：** 规划图；机制细节以 docs/technology-comparison.md、docs/system-design.md、docs/database-design.md 和 docs/communication-protocol.md 为准。

~~~mermaid
flowchart TD
    NEED["业务需求：多人同时操作同一房间"]
    AUTH["每房间一个权威写入顺序"]
    TX["数据库事务提交状态、事件与幂等结果"]
    ORDER["对象 version + 房间 sequence"]
    PUSH["WebSocket 推送授权后的事件"]
    RECOVER["持久事件日志 + 快照"]
    RETRY["operationId 幂等重试"]
    PRIVACY["服务端按成员权限过滤状态"]

    NEED --> AUTH
    AUTH --> TX
    TX --> ORDER
    TX --> RETRY
    TX --> PUSH
    PUSH -->|"连接可能断开或通知可能丢失"| RECOVER
    RECOVER -->|"按序补发或快照恢复"| PUSH
    AUTH --> PRIVACY
    PRIVACY --> PUSH
~~~

**图示说明：**
- 事务是权威状态与事件记录的提交边界。
- version 用于对象冲突检测，sequence 用于房间内已提交事件排序，operationId 用于重试去重。
- WebSocket 是实时传播通道；持久事件日志与快照承担恢复职责。
- 服务端权限过滤必须覆盖实时事件与恢复快照。
