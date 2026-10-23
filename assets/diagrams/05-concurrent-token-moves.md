# 图 5：同一标记的并发移动与版本冲突

**用途：** 用一个具体场景说明房间内的权威排序和对象版本检查如何共同工作。  
**建议报告位置：** 第 6 章“同步”。  
**状态：** 机制示例；错误处理文案和重试体验待接口实现时确认。

~~~mermaid
sequenceDiagram
    autonumber
    participant A as 玩家 A
    participant B as 玩家 B
    participant R as 房间协调者
    participant D as PostgreSQL
    Note over A,B: 两位玩家都读取到 token.version = 7
    A->>R: 移动标记，expectedObjectVersion=7
    B->>R: 移动标记，expectedVersion=7
    R->>D: 串行处理 A 的操作并校验版本 7
    D-->>R: 更新成功：token.version=8，internal roomSequence=108
    R-->>A: SUCCEEDED，objectVersion=8；事件稍后进入各自授权视图
    R->>D: 处理 B 的操作并校验 expectedVersion=7
    D-->>R: 当前对象版本已是 8，拒绝过期修改
    R-->>B: CONFLICT，返回当前版本与刷新建议
~~~

**关键说明：**
- 对象版本用于发现“客户端基于过期对象状态写入”的冲突。
- 内部 roomSequence 用于排列完整房间事件流，不等同于对象版本，也不直接暴露为客户端连续序号。
- 权限过滤后，客户端使用 deliverySequence 检查自己的可见流；中间内部事件不可见时，不应触发假缺口。
- 被拒绝的过期操作不应推进成功事件序号，也不应覆盖已经提交的新状态。
- 若产品决定自动重试，必须先重新读取最新状态并重新校验业务意图，不能盲目重复旧坐标。
