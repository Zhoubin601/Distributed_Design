# 任务深度分析与方案构想 (analysis-notes.md)

> **状态警告：历史候选材料，已被当前设计基线取代。** 本文件较早版本提出过 CRDT/P2P、WebRTC、Kafka、Redis Redlock、应用层 Quorum 以及跨服务 2PC 等方案；这些内容不代表当前系统采用的技术，也不得直接拼入最终报告。当前以 `docs/plan.md`、`docs/technology-comparison.md`、`docs/system-design.md`、`docs/database-design.md`、`docs/communication-protocol.md` 和 `docs/design-consistency-review.md` 为准。未在这些文件中明确锁定的机制一律视为候选或待确认。

## 1. 任务性质与目标定位

本任务为东北大学软件学院《分布式系统导论》（宋杰老师主讲）的期末大作业报告撰写。
作业核心目标是**完成一份工程级、高规格的分布式系统概要设计说明书**，最终必须交付符合 `raw/课程设计模板.docx` 严格规范的 Word 文档（`.docx`）。

新增资料（《测验方法.pptx》、宋杰老师 502 页完整课件、Tanenbaum 中英文教材）进一步明确了以下核心导向：
1. **严格的行政交付规则**：
   - 团队规模严格限制为 **4 ~ 8 人**（不接受少于4人，不接受多于8人）；
   - 组内按角色贡献率分配（组长 100%、副组长 98%、组员 80%）；
   - **截止时间：11月23日 24:00 前**，发送至 `sy_songjie@163.com`，邮件名 `A_组名` 或 `B_组名`；
   - **只收一次，以第一个附件为准，不许替换**（必须做到交稿即终版，零排版瑕疵，零逻辑漏洞）。
2. **知识点覆盖要求（拿满 15% 完整度分）**：
   - 必须全面对齐宋杰老师 502 页教学课件中的核心模型与机制；
   - 老师在 PPT 中明确说明：“**我给出的目录是参考，可以自己修改**”。模板中给出的 1~7 章覆盖了课件 Chapter 1~7，而课件中还有重要的 **Chapter 8 Fault Tolerance（容错性）**。我们可以在报告中新增或有机融入“容错性与故障恢复”独立章节或子项（包含故障检测、RPC 幂等重试、状态机故障恢复），从而向评阅老师展现超越模板的“全知识点覆盖”。
3. **查重防线**：
   - 严禁抄袭往届学生作业（宋老师明确表示会比对查重库）。
   - 必须坚持原创架构推演，大段引述概念必须带有规范上角标 `[x]` 并对应参考文献。

---

## 2. 两个备选系统的对比分析（A 协同设计 vs B 虚拟桌游）

| 维度 | 选项 A：多人实时协同设计与原型平台 (对标 Penpot) | 选项 B：多人实时协作在线虚拟桌游平台 (对标 Owlbear Rodeo) |
| :--- | :--- | :--- |
| **真实参考物** | Penpot (Clojure/Rust/WebAssembly 开源项目) | Owlbear Rodeo (TypeScript/WebRTC/Svelte) |
| **核心业务实体** | 复杂树形画板（Canvas）、图层节点（Layer）、组件符号（Component）、矢量路径 | 房间（Room）、地图底图（Scene）、Token标记（Token）、迷雾遮蔽（Fog of War）、掷骰子记录 |
| **协同特征** | 高并发树状图元编辑、多属性并发修改、矢量几何计算 | 空间网格离散定位、高频光标/移动、基于视锥/权限的差分视野（Fog）、点对点或星型轻量广播 |
| **一致性复杂度** | **极高**（树形结构并发移动/重亲父子关系的 CRDT 实现难度大，但也极好展现学术水平） | **高**（离散对象状态较独立，CRDT 或状态同步更直观易讲透，迷雾与视野权限增色明显） |
| **通信与拓扑** | 典型 C/S 集中式架构，通过协同网关分发，便于实现全局快照与版本控制 | C/S 与 P2P (WebRTC Mesh) 混合架构，轻服务端中继甚至无状态边缘中继，非常契合分布式网络专题 |
| **得分优势分析** | 工业感强，参考资料详实（Penpot 架构公开可查），适合做深度微服务和复杂持久化设计 | 场景趣味性强，天然自带逻辑时钟（回合制/掷骰事件）、空间命名、权限隔离，给评阅老师眼前一亮的感觉 |

---

## 3. 宋杰老师课件与报告章节的深度融合设计

报告必须严格将宋老师 502 页 PPT 中的经典理论与实际协同系统做有机绑定：

### 2. 体系结构 (Architectures)
- **课件理论对应**：软件架构风格（分层 Layered、基于事件 Event-based、共享数据空间 Shared Data-space）；系统架构（三层架构 Three-tier、客户端-服务器 C/S、覆盖网络 Overlay Network、边缘服务器 Edge-Server、协同分布式系统 Collaborative Systems）。
- **概要设计映射**：
  - 接入层（Edge/Gateway）：边缘反向代理，TLS 终止与负载均衡。
  - 协作层（Session Workers）：基于一致性哈希路由的动态房间/画布有状态微服务。
  - 核心服务集群（Stateless Microservices）：用户鉴权、团队权限、资产管理无状态服务。
  - 存储层（Storage Tier）：分布式数据库（PostgreSQL）+ 分布式缓存（Redis Cluster）+ 分布式对象存储（S3/MinIO）。

### 3. 进程 (Processes)
- **课件理论对应**：多线程客户端（Multi-threaded Client）、多线程服务器（Multi-threaded Server / Worker pool）、胖客户端 vs 瘦客户端（Fat vs Thin client）、服务器集群（Server Clusters）、TCP Handoff、代码迁移（Code Migration）。
- **概要设计映射**：
  - 客户端：采用**胖客户端 (Fat Client)** 架构，主渲染线程 + Web Worker / WebAssembly 后台并发计算线程（运行本地 CRDT、网络数据包编解码），避免高频协同造成 UI 卡顿。
  - 服务端：采用 Reactor 事件循环与线程池并发模型；容器化无状态集群（Kubernetes Pods 弹性伸缩）；有状态会话节点间基于 TCP Handoff / 反向代理长连接平滑漂移。

### 4. 通信 (Communication)
- **课件理论对应**：协议分层、中间件协议；远程过程调用（RPC Client/Server Stubs、异步 RPC、延迟同步 RPC）；面向消息的通信（Sockets、消息队列 MQ 架构、瞬态与持久通信、发布-订阅模式 Pub/Sub）。
- **概要设计映射**：
  - 客户端与服务端：WebSocket 全双工长连接（持久可靠传输协作操作指令）+ WebRTC DataChannel（瞬态非可靠高频数据，如光标位置、视锥漫游）。
  - 服务端内部：gRPC 二进制微服务通信（强类型 IDL、高效 Stub 桩代码）；Kafka / Redis Pub/Sub 异步事件解耦（操作日志回放、协同快照归档）。
  - 大文件传输：S3 Presigned URL + 分块断点续传。

### 5. 命名 (Naming)
- **课件理论对应**：命名空间（Name Space）；扁平命名（广播、转发指针、家乡位置、DHT/Chord）；结构化命名（树状名称空间、DNS 递归与迭代解析）；基于属性的命名（Directory services、LDAP）。
- **概要设计映射**：
  - 实体命名（扁平）：全局图元/用户/房间采用 UUIDv4 或 Snowflake（分布式雪花算法）生成全局唯一 ID。
  - 层次与空间命名（结构化）：项目与资产组织采用 URI 层次命名（`/org/{id}/workspace/{id}/project/{id}/room/{id}`）；画板/地图图元采用空间 R-Tree / QuadTree 网格四叉树编码寻址。
  - 服务发现与定位：基于 Kubernetes CoreDNS 与 Consul 实现微服务实例注册、健康检查与动态寻址。

### 6. 同步 (Synchronization)
- **课件理论对应**：物理时钟同步（NTP 协议、网络往返时延估计）；逻辑时钟（Lamport 逻辑时钟与偏序关系、向量时钟 Vector Clock 与因果并发判定）；分布式互斥（基于权限的 Lamport 算法、基于令牌环 Token Ring、中心化互斥）；选举算法（Bully 欺负算法、环算法 Ring Algorithm）。
- **概要设计映射**：
  - 时钟校准：节点间 NTP 物理时钟粗校准。
  - 因果排序：针对无中心弱网环境下的并发协同编辑，采用**向量时钟 (Vector Clock)** 或 **Lamport 时间戳** 标记每个操作的偏序关系，解决网络抖动导致的操作倒序重放问题。
  - 互斥与租约：图元独占锁定（避免多用户同时进行包围盒变形等破坏性操作），采用带 TTL 的分布式租约锁（Redis Redlock / 分布式锁服务）；主协调节点故障时采用改进的 Bully 或 Raft 领导者选举。

### 7. 一致性与复制 (Consistency and Replication)
- **课件理论对应**：连续一致性（Conits 度量）；以数据为中心的一致性模型（严格一致性、顺序一致性、因果一致性、最终一致性 Eventual Consistency）；以客户为中心的一致性模型（单调读 Monotonic Reads、单调写 Monotonic Writes、读自身写 Read-Your-Writes、写跟随读 Writes-Follow-Reads）；复制协议（基于主备份 Primary-Backup、本地写 Local-Write、基于仲裁 Quorum 投票机制）。
- **概要设计映射**：
  - 一致性模型：支持“读自身写”与“单调写”的客户端本地优先（Local-First）体验；全局保证**强最终一致性 (Strong Eventual Consistency, SEC)**。
  - 并发冲突解决：采用现代无冲突复制数据类型 **CRDT (Conflict-free Replicated Data Type)**（状态 CRDT 与操作 CRDT），各客户端本地无锁即时应用，网络收敛后数学可证明状态一致。
  - 副本与持久化：协作服务器采用内存双机热备（Primary-Backup 模型）；持久存储层采用 Quorum 仲裁读写（$N, R, W$ 满足 $R+W > N$ 且 $W > N/2$）保证数据不丢失。

### 8. 容错性与故障恢复 (Fault Tolerance) —— 关键加分项
- **课件理论对应**：故障模型（Crash-stop, Crash-recovery, Byzantine failure）；k-容错与拜占庭协定；RPC 故障语义与幂等重试（Idempotent requests）；可靠成组通信与虚拟同步（Virtual Synchrony）；分布式两阶段提交（2PC）。
- **概要设计映射**：心跳故障探测机制、客户端离线断网重连与操作队列本地暂存、幂等序列号防重、分布式两阶段提交保障跨服务资产事务一致性。

---

## 4. 下一步行动计划

1. 确认最终选题（A 或 B）。
2. 获取团队具体信息（组名、成员名单、学号、分工角色）。
3. 按照模板结构产出详尽的概要设计大纲与正文草稿，并生成工程架构图与时序图。
4. 严格按照排版要求（五号宋体、0.15行间距、三线表、仿宋加粗图表注、参考文献角标、附录不变）生成最终 Word 交付物。


---

## 5. 用户确认选题与课程理论来源（2026-10-23）

用户已确认选择 **B：多人实时协作的在线虚拟桌游平台（参考 Owlbear Rodeo）**，偏好为工作量可控、设计逻辑清晰、讲透课堂知识。

**资料职责必须区分：**
- `raw/Introduction to Distributed System-by JieSong NEU.pdf` 是宋杰老师课堂使用的分布式系统理论课件，是 Chapter 1–8 理论、模型和算法映射的主要依据。
- `raw/测验方法.pptx` 用于核对作业评分、组队、提交等要求，不是课程理论课件。
- `raw/要求.txt` 用于核对受限选题和评分维度。
- `raw/课程设计模板.docx` 与 `raw/不允许修改附录.jpg` 用于正式报告格式与附录限制。

方案原则：需求范围保持适中；逐章覆盖课程 Chapter 1–8；每个知识点都说明概念、桌游场景映射、方案选择与替代方案/不采用理由。CRDT、P2P、Quorum、2PC/3PC 等不默认全部进入核心实现，须根据课程原文和评分要求决定是采用还是比较。

当前规划基线见 `docs/plan.md`；其中性能指标均为待确认的设计建议，不是课堂硬性指标或实测数据。最终 Word 尚未生成。
