# 图 6：客户端断线重连与事件恢复

**用途：** 区分授权事件补发、快照恢复和在线水位对账。  
**建议报告位置：** 第 8 章“容错与恢复设计”。  
**状态：** 与当前通信协议的游标和可见事件流模型对齐；对账频率仍待确认。

~~~mermaid
flowchart TD
    A["重新连接<br/>发送 resumeCursor、lastDeliverySequence、viewVersion"]
    B["重新验证身份、成员状态与当前权限"]
    C["从 resumeCursor 扫描内部 roomSequence 并生成授权投影"]
    D{"游标有效且 viewVersion 未变化？"}
    E["按 deliverySequence 连续补发可见事件"]
    F["发送当前权限下的新快照<br/>重置视图事件进度"]
    G["SYNC_WATERMARK<br/>latestDeliverySequence + resumeCursor"]
    H{"客户端可见流是否落后？"}
    I["继续补发并对账"]
    J["恢复完成"]
    A --> B --> C --> D
    D -- 是 --> E --> G --> H
    D -- 否 --> F --> E
    H -- 是 --> I --> G
    H -- 否 --> J
~~~

**关键说明：**
- 只有当前仍有房间访问权限的客户端才可以恢复该房间状态。
- 快照的状态内容与 snapshotSequence 必须对应同一一致性视图。
- 快照必须按当前权限生成；不能把含完整隐藏区域的内部状态发给普通玩家。
- 如果客户端发现序号缺口或状态校验失败，不应静默跳过缺失事件。
