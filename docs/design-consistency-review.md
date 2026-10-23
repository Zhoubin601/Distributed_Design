# 技术设计一致性审查报告

> 审查范围：docs/plan.md、docs/system-design.md、docs/technology-comparison.md、docs/communication-protocol.md、docs/database-design.md、docs/failure-scenarios.md、两个核心场景审查文档及 assets/diagrams/ 中的相关图源。  
> 审查性质：文档逻辑审查；没有执行系统代码、压测或故障演练。  
> 结论：核心架构方向可以保留，但事件投影/恢复游标、版本字段语义和候选技术的基线状态必须统一后，才适合进入最终 Word 整合。

## 1. 发现的问题与处理结果

| 优先级 | 问题 | 风险 | 本轮处理 |
|---|---|---|---|
| P0 | **内部 roomSequence 与战争迷雾权限过滤冲突** | 若客户端直接检查全房间 sequence 是否连续，隐藏事件会制造“假缺口”；暴露内部 sequence 也可能泄露隐藏活动的数量/节奏 | 已统一为：数据库内部 roomSequence 排序完整日志；权限投影后的客户端流使用连续 deliverySequence，并绑定 viewVersion |
| P0 | **最后一条通知丢失可能永远不触发补发** | 只在收到更大 sequence 时检查缺口，无法发现没有后续事件的尾部丢失 | 已增加 SYNC_WATERMARK/心跳周期对账；网关从 resumeCursor 扫描持久事件，检测客户端落后后补发 |
| P1 | **expectedVersion 的含义与其他文档不一致** | system-design 将其描述为房间版本，协议和数据库实际按对象版本校验 | 已统一为 expectedObjectVersion；它只用于目标对象冲突检测，不等同于内部 roomSequence |
| P1 | **通知发布与每个客户端收到消息的语义混在一起** | published_at 只能表示通知已交给通知通道，不能证明所有在线客户端收到 | 已明确 Redis Pub/Sub 仅作唤醒/传播信号；持久事件扫描和水位对账承担恢复 |
| P1 | **outbox 方案状态不一致** | 一处允许独立 outbox 或扫描事件表，另一处已经定义 published_at/publish_attempts/next_attempt_at | 当前基线采用 room_event 上的待发布字段作为重试元数据；不另设独立 outbox 表，除非后续实现需要重新评估 |
| P1 | **租约/epoch 被一处写成候选、另一处写成已确定机制** | 可能让最终报告把未验证的故障切换写成已保证的高可用 | 统一为概要设计提案：每次权威写事务应校验 owner_instance、epoch、lease_until；具体续期、接管参数和故障演练仍待确认 |
| P2 | **观察者角色的范围不明确** | 规划暂不纳入额外角色，但设计图中出现观察者视图 | 已将观察者标为可选且待确认；当前核心角色仅为主持人与普通玩家 |
| P2 | **性能假设没有完整进入待确认清单** | system-design 额外出现 100 个活跃房间与 API P95 500 ms，容易被误当成已确认需求 | 已将 100 房间、300 ms 更新延迟、500 ms API 延迟、5 秒恢复目标统一列入 questions.md，全部仍待用户确认 |
| P2 | **早期分析文件仍包含与当前基线冲突的技术** | CRDT/P2P、WebRTC、Kafka、Redlock、Quorum 和跨服务 2PC 可能被 Codex 当作最终方案 | 已在 analysis-notes.md 顶部加历史材料警告，明确当前基线文档优先级 |
| P2 | **技术比较文档中的第 1 章标题已过时** | 与模板对齐后的“系统简介”名称不一致 | 已更新为“第 1 章 系统简介” |

## 2. 当前建议锁定的技术基线

1. **架构：** 分层客户端—服务器；不同房间可由不同实例处理，同一房间通过单一权威写入路径定义操作顺序。
2. **权威数据：** PostgreSQL 保存权威状态、完整房间事件日志、幂等操作结果、快照和协调者租约。
3. **事务：** 状态变更、内部 roomSequence、成功事件与操作结果在同一数据库事务内提交。
4. **并发控制：** expectedObjectVersion 检查目标对象是否过期；内部 roomSequence 为完整房间日志排序。二者不能混用。
5. **客户端事件：** 服务端先按当前成员权限生成投影，再分配连续 deliverySequence。客户端不直接接收完整内部事件载荷或内部 roomSequence。
6. **恢复：** resumeCursor 指向已扫描的内部日志位置，并绑定 roomId、成员和 viewVersion；权限视图变化时旧游标失效，客户端获取新快照。
7. **尾部丢失检测：** Redis 通知只是提示网关检查新事件；周期性 SYNC_WATERMARK/对账用于发现最后一条通知丢失、后续没有新事件的情况。
8. **事件发布：** 当前设计使用 room_event 的 published_at、publish_attempts、next_attempt_at 作为待发布重试元数据；通知通道不代表客户端送达。
9. **协调者隔离：** 持久租约 + epoch/fencing 是建议的高层设计提案；只有每次权威写事务校验 owner_instance、epoch 和租约有效性，才有旧任期隔离意义。
10. **明确不纳入核心：** 全 P2P/CRDT 合并、WebRTC 光标通道、Kafka/RabbitMQ、应用层 Quorum、每次移动的分布式互斥，以及单数据库事务内的 2PC/3PC。它们可以用于课程比较，但不应全部堆入最终方案。

## 3. 仍待确认，不应被写成已决定的需求

- 每房间 2–8 人、约 100 个活跃房间。
- 同地域正常网络下，从权威提交到授权客户端收到更新的 P95 ≤300 ms。
- 常规 API P95 ≤500 ms（不含地图文件传输）。
- 网络恢复后普通规模房间状态恢复目标 ≤5 秒。
- 地图是只选择预置资源，还是支持用户上传。
- 是否需要观察者角色；当前建议核心范围只包含主持人与普通玩家。
- PostgreSQL 的备份、同步/异步复制、RPO/RTO。
- 租约期限、续期周期、故障接管与数据库故障时的写入策略。
- 快照频率、事件保留期限、对账频率，以及游标签发/失效规则的具体实现。

## 4. Codex 整合前验收清单

- [ ] 正文只把内部 roomSequence 用作服务端完整日志排序，不把它当作客户端可见事件的连续序号。
- [ ] 客户端可见事件使用 deliverySequence；事件、快照和恢复游标都绑定当前权限视图。
- [ ] 权限变化时，旧 viewVersion/cursor 失效并生成新的授权快照。
- [ ] 通知丢失时，在线周期对账能发现尾部事件丢失；离线重连能从 resumeCursor 补发。
- [ ] expectedObjectVersion、roomSequence、deliverySequence、resumeCursor、viewVersion、operationId、epoch 各自语义清楚。
- [ ] 不把租约/epoch、性能指标或复制能力描述成已实现、已测试或有无条件保证。
- [ ] 最终报告仍按课程模板组织；图表只挑选最能解释设计的 5–6 张。
- [ ] 原始 raw/ 资料保持不变。

**审查结论：** 核心方向无需推翻。最重要的改动是把“完整内部事件流”与“按权限过滤后的客户端事件流”分开，并增加周期水位对账。完成本轮文档对齐后，下一步仍应由用户确认需求范围和指标，再进入最终报告整合。
