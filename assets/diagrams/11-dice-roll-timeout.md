# 图 11：掷骰结果已提交但响应丢失

**用途：** 解释网络响应丢失后，客户端为什么不能直接认定操作失败，以及稳定 operationId 如何让重试返回原结果。  
**建议报告位置：** 第 4 章“通信”或第 8 章“容错”。  
**状态：** 概要设计示意，不代表系统已实现或测试。

~~~mermaid
sequenceDiagram
    autonumber
    participant C as 玩家客户端
    participant S as 房间服务
    participant D as 持久化存储
    participant P as 事件发布器
    participant R as 房间成员

    C->>S: ROLL_DICE（operationId=R1，规则=d20）
    S->>S: 验证身份、权限与规则
    S->>D: 检查 R1，保存结果、事件与操作记录
    D-->>S: 提交成功：结果=17，内部 roomSequence=205
    S--xC: COMMAND_RESULT（17）响应丢失
    P->>D: 读取已提交的待通知事件
    D-->>P: 内部掷骰事件 roomSequence=205，结果=17
    P-->>R: 网关扫描事件并生成授权投影，deliverySequence 连续递增
    Note over C: 客户端超时，无法判断是否提交
    C->>S: 使用原 operationId=R1 重试
    S->>D: 查询原操作结果
    D-->>S: 已提交结果=17
    S-->>C: 返回 17，不重新掷骰
~~~

**图示要点：**

- 超时不等于操作失败；服务端可能已提交，只是响应丢失。
- 同一个 operationId 重试时，服务端返回原操作结果。
- 持久事件和异步通知触发网关扫描；客户端只接收当前权限下的投影与 deliverySequence。周期水位对账可发现尾部通知丢失。
- 目标是避免重复副作用，不是声称网络实现“恰好一次投递”。
