# 原始资料摘录与分析笔记 (source-notes.md)

## 1. 完整资料清单与来源

| 文件名 | 类型 | 核心内容概要 |
| :--- | :--- | :--- |
| `raw/测验方法.pptx` | 官方PPT | **【新增】** 明确分组人数（4-8人）、分工贡献率分值（组长100%/副组长98%/组员80%）、邮箱提交格式（`A_组名`或`B_组名`）、**截止时间：11月23日24:00**、仅限提交一次不许替换、明确说明“目录是参考，可以自己修改”。 |
| `raw/Introduction to Distributed System-by JieSong NEU.pdf` | 课程课件 (502页) | **【新增】** 东北大学宋杰老师《分布式系统导论》官方完整教学课件。涵盖 01导论、02体系结构、03进程、04通信、05命名、06同步、07一致性与复制、08容错性 全部理论细节与算法模型。 |
| `raw/00-分布式系统-原理与范型(第2版).pdf` | 经典教材 (中文) | **【新增】** Tanenbaum 经典中译本教材，提供标准学术术语、定义与理论推导参考。 |
| `raw/00-Distributed System-Principle and Paradigms (2nd Edition).pdf` | 经典教材 (英文) | **【新增】** Tanenbaum 原版英文教材，供英文参考文献标准引用及原文术语核对。 |
| `raw/要求.txt` | 纯文本 | 期末大作业核心要求、两大受限选题范围（A协同设计/B虚拟桌游）、五大评分维度及格式规范。 |
| `raw/课程设计模板.docx` | Word文档模板 | 官方标准排版格式、固定章节骨架、正文五号宋体/单倍行距/0.15行距、三线表、图注表注规范、参考文献及附录考核表。 |
| `raw/不允许修改附录.jpg` | 课堂投影照片 | 明确指出文末“附录”表格的填写规范：结构不得改动、不得用回车、得分栏勿填、必填组名/系统名/人员学号。 |
| `raw/penpot.jpg` | 课堂投影照片 | 选题A参考系统：Penpot（https://penpot.app/），开源在线协同设计与原型制作平台。 |
| `raw/Owlbear.jpg` | 课堂投影照片 | 选题B参考系统：Owlbear Rodeo（https://www.owlbear.rodeo/），轻量级浏览器虚拟桌游（VTT）多人协作平台。 |

---

## 2. 大作业考核与行政管理硬性规定（来自《测验方法.pptx》）

1. **分组人数限制**：
   - **4 ~ 8 人**（必须自由组队，不接受少于4人，不接受多于8人；降级/重修需单独联系）。
2. **成绩评定与组内分配机制**：
   - 整组得分区间：**75 至 100 分**。
   - 按成员角色及贡献率折算个人最终得分：
     - **组长（1人，必选）**：按整组得分的 **100%** 计分；
     - **副组长（最多3人）**：按整组得分的 **98%** 计分；
     - **组员（最多4人）**：按整组得分的 **80%** 计分。
   - 同一同学若出现在多组，按最低分（80%）计算。
3. **提交与截止要求**：
   - **截止时间**：**11月23日 24:00 前**。
   - **接收邮箱**：`sy_songjie@163.com`。
   - **邮件主题命名格式**：`A_组名` 或 `B_组名`（严格按照所选题目方向 A 或 B 命名）。
   - **提交铁律**：“**只收一次，以第一个附件为准，以后不许替换**”。因此提交前必须彻底检查，确保最终版毫无破绽。
4. **查重防抄袭**：
   - 保持原创，宋杰老师会与往届学生及网络大段文献做严格比对。大段抄袭且不加引用的对应项按 0 分计。
5. **目录灵活性**：
   - PPT 明确标注：“**我给出的目录是参考，可以自己修改**”。但必须全面涵盖所学知识点。

---

## 3. 选题范围校对澄清

- 在《测验方法.pptx》的 Slide 2 中列出了早期或往届的参考选项（直播购物、线上约车、大型在线考试），但**在 2026.10.22 课堂最新现场投影（`penpot.jpg` 和 `Owlbear.jpg`）以及《要求.txt》中，宋杰老师已经将本学期选题确定并收敛为以下两个系统二选一**：
  - **A：多人实时协作的在线设计与原型平台**（以 Penpot 为原型）
  - **B：多人实时协作的在线虚拟桌游平台**（以 Owlbear Rodeo 为原型）
- 在《测验方法.pptx》第 8 页关于邮件命名的规定中，也只允许写 `A_组名` 或 `B_组名`，完全对应上述 A、B 两个系统。

---

## 4. 宋杰老师课件（502页）知识点映射清单（必须覆盖）

要拿满“设计完整：涵盖所有所学知识点 (15%)”和“自主知识运用 (20%)”，报告各章节必须紧密结合宋老师 502 页 PPT 中的关键知识点：

| 章节 | 对应课件章节 | 必须引用的宋老师课件核心概念与理论模型 |
| :--- | :--- | :--- |
| **2. 体系结构** | `02-Architectures` | 软件架构风格（分层、基于事件、共享数据空间）；系统架构（三层架构、C/S 与 P2P 混合、覆盖网络 Overlay Network、超节点 Superpeers、边缘服务器 Edge-Server、协同分布式系统） |
| **3. 进程** | `03-Processes` | 多线程客户端（Web Browser）与多线程服务器；胖/瘦客户端（Fat vs Thin client）；服务器集群（Server Clusters）与 TCP Handoff；代码迁移（弱移动性/强移动性、Push/Pull资源迁移） |
| **4. 通信** | `04-Communication` | 分层协议与中间件协议；RPC 原理（客户端/服务端 Stub、异步 RPC、延迟同步 RPC）；基于消息的通信（套接字 Sockets、消息队列 MQ 架构、瞬态与持久通信、发布-订阅模式） |
| **5. 命名** | `05-Naming` | 命名空间（Name Space）；扁平命名（广播、转发指针、基于家乡代理、分布式哈希表 DHT/Chord）；结构化命名（名称解析、递归/迭代查找、DNS 命名空间）；基于属性的命名（LDAP、资源描述） |
| **6. 同步** | `06-Synchronization` | 时钟同步（NTP 协议、物理时钟偏差）；逻辑时钟（Lamport 逻辑时钟、向量时钟 Vector Clock）；分布式互斥（基于权限的 Lamport/Ricart-Agrawala 算法、基于令牌环的 Token Ring、中心化互斥）；选举算法（Bully 欺负算法、环算法 Ring Algorithm） |
| **7. 一致性与复制** | `07-Consistency & Rep.` | 连续一致性（Conits 度量）；以数据为中心的一致性（顺序一致性、因果一致性、最终一致性）；以客户为中心的一致性（单调读、单调写、写跟随读、读自身写）；副本放置与内容分发；一致性协议（基于主备份 Primary-Backup 协议、本地写 Local-Write、基于仲裁 Quorum 机制） |
| **8. 容错性（可扩展）**| `08-Fault Tolerance` | 故障模型（故障停止、拜占庭故障）；进程容错（k-容错、拜占庭协定）；RPC 故障语义与幂等重试；可靠成组通信与虚拟同步（Virtual Synchrony）；分布式提交（2PC 两阶段提交、3PC） |


## 2026-10-24 最新报告复核来源补记

- 来源名称：课程作业当前要求；文件名：`raw/要求.txt`；引用日期：2026-10-24。要求对限定 A/B 选题作概要设计，并清晰定义需求、覆盖所学知识、论证正确性、体现自主运用及良好排版。
- 来源名称：官方课程设计模板；文件名：`raw/课程设计模板.docx`；引用日期：2026-10-24。直接读取正文及附录结构；模板附录与报告的网格合并关系相同，但列宽有变化。
- 来源名称：测验方法；文件名：`raw/测验方法.pptx`；引用日期：2026-10-24。直接读取幻灯片，核实 4–8 人、仅交一次及目录可调整；第 2 页旧选题不替代当前 `要求.txt`。
- 来源名称：附录课堂投影；文件名：`raw/不允许修改附录.jpg`；引用日期：2026-10-24。直接视觉核对，得分栏不填、系统名及人员栏需真实填写；照片未提供允许修改列宽的文字说明，此解释待确认。
- 来源名称：宋杰修改的课程课件；文件名：`raw/Introduction to Distributed System-by JieSong NEU.pdf`；引用日期：2026-10-24。页脚标示 Modified ... 2014；报告参考文献 [1] 的 2024 年缺少原始资料支持。物理页 261 讲属性命名/目录服务，319–334 讲选举，346–350 讲连续一致性/Conit，370 讲单调读。相关摘录保存于 `docs/review-20261024/course-excerpts.txt`。
- 本次联网仅执行项目 Git 更新，没有新增外部理论或文献来源。详细检查见 `docs/20261024-report-requirements-review-v1.md`。


## 2026-10-24 第二轮检查补记

来源名称：用户手动修改的 v2；文件名：`output/v2/Distributed_Design_Report_Draft_v2.docx`；引用日期：2026-10-24。封面及附录团队表已填完；技术正文与参考文献文本较第一轮未变。课程要求仍按第一轮列出的 raw 原始资料，不使用新增外部来源。


## 2026-10-24 v3 生成来源及核对

- 来源名称：用户手动修改的 v2；文件名：`output/v2/Distributed_Design_Report_Draft_v2.docx`；引用日期：2026-10-24。保留封面和团队填写，原文件哈希未变。
- 来源名称：官方课程设计模板及附录限制；文件名：`raw/课程设计模板.docx`、`raw/不允许修改附录.jpg`；引用日期：2026-10-24。附录重新使用模板表本体，填入原有资料，保持合并、字段、边框及模板自动布局。Word 保存时会自动重算列宽，不能等同于人为增删结构。
- 来源名称：课程要求及测验办法；文件名：`raw/要求.txt`、`raw/测验方法.pptx`；引用日期：2026-10-24。选题 B、概要设计深度、评分、人数及教师空栏要求。资料未规定报告最低页数。
- 来源名称：宋杰修改的分布式系统课件；文件名：`raw/Introduction to Distributed System-by JieSong NEU.pdf`；引用日期：2026-10-24。直接核对 RPC、流与多播、属性命名、Bully/环选举、Conit、四种客户端模型、复制管理和容错。原文页号与摘录保存于 `docs/v3-work/course-verification.txt`。参考文献 [1] 使用课件标示的修改年 2014；不把元数据创建年当出版年。
- 图 5、图 6 为按本次设计推导自绘，来源是报告的权限投影和快照恢复规则，不冒充课件原图。没有新增联网文献。

## 2026-10-24 拉取最新后的独立复核来源

- 来源名称：当前作业要求、课程模板、测验方法及附录限制；文件名：`raw/要求.txt`、`raw/课程设计模板.docx`、`raw/测验方法.pptx`、`raw/不允许修改附录.jpg`；引用日期：2026-10-24。本轮直接复读并对照本地 v3，不依赖历史结论代替原始要求。
- 来源名称：课程理论课件；文件名：`raw/Introduction to Distributed System-by JieSong NEU.pdf`；引用日期：2026-10-24。直接抽查物理页 1、155、261、319、321、346–350、370，摘录留在 `docs/20261024-v3-recheck-v1/local-course-excerpts.txt`。
- 来源名称：本地 v3、手动 v2 及远程旧版；文件名：`output/v3/20261024-misttable-distributed-design-v3.docx`、同名 PDF、`output/v2/Distributed_Design_Report_Draft_v2.docx`、`origin/main:output/Distributed_Design_Report_Draft_v2.docx`；引用日期：2026-10-24。本地 v3 无占位标记，远程旧版仍有 29 处；封面及附录人员值与手动 v2 一致。只记录核验结果，不在长期背景中重复保存个人信息。
- 本轮网络操作仅更新 Git；没有新增外部理论资料，未逐篇联网核实全部参考文献。raw 和 output 审查前后文件哈希清单相同。

## 2026-10-24 文献实质核验补记

用户本轮明确授权实际访问 Owlbear Rodeo 并核实全部文献对论述的支持关系。以下均为本次引用/访问日期 **2026-10-24**，逐条位置、边界及修订见 `docs/20261024-reference-support-audit-v1.md`。

| 来源名称 | 链接或文件名 | 核验用途 |
|---|---|---|
| 官方课件及英文第二版教材 | `raw/Introduction to Distributed System-by JieSong NEU.pdf`；`raw/00-Distributed System-Principle and Paradigms (2nd Edition).pdf` | [1,2]；物理页 498–501 的 3PC；教材印刷页 363–365 的恢复分类 |
| Lamport 原文 | https://lamport.azurewebsites.net/pubs/time-clocks.pdf | [3]；偏序与逻辑时钟 |
| Gifford 原文 | https://www.cs.sfu.ca/~vaughan/teaching/431/papers/gifford79.pdf | [4]；加权读写仲裁与版本 |
| Ricart / Agrawala 原文 | https://courses.grainger.illinois.edu/cs425/fa2023/358527.ricart-agrawala.pdf | [5]；互斥、消息数及正确页码 9–17 |
| Mattern 原文及作者元数据 | https://vs.inf.ethz.ch/publ/papers/VirtTimeGlobStates.pdf ；https://vs.inf.ethz.ch/publ/bibtex.html?file=papers%2FVirtTimeGlobStates | [6]；向量时间及论文集名称 |
| Fielding 学位论文 | https://www-test.ics.uci.edu/~fielding/pubs/dissertation/top.htm ；https://www-test.ics.uci.edu/~fielding/pubs/dissertation/net_arch_styles.htm | [7]；分层 C/S 风格 |
| RFC Editor | https://www.rfc-editor.org/rfc/rfc6455 | [8]；WebSocket 双向通信能力 |
| Owlbear 官网与官方文档 | https://www.owlbear.rodeo/ ；https://docs.owlbear.rodeo/docs/getting-started/ ；https://docs.owlbear.rodeo/docs/rooms/ ；https://docs.owlbear.rodeo/docs/fog/ | [9]；实际访问日期，房间/地图/标记/迷雾场景 |
| Gray 原文、作者书目与出版社 | https://jimgray.azurewebsites.net/papers/dbos.pdf ；https://jimgray.azurewebsites.net/jimgraypublications.htm ；https://link.springer.com/chapter/10.1007/3-540-08755-9_9 | [10]；事务与 2PC，补全书目信息 |
| Chandy / Lamport 原文 | https://lamport.azurewebsites.net/pubs/chandy.pdf | [11]；全局截面和通道状态，仅作理论对照 |
| Vogels 期刊原件及作者公开版本 | https://15799.courses.cs.cmu.edu/fall2013/static/papers/p40-vogels.pdf ；https://www.allthingsdistributed.com/2008/12/eventually_consistent.html | [12]；实际读取期刊版 pp. 42、44 的客户端一致性及版本防回退 |
| Shapiro 等原文及出版方 | https://perso.lip6.fr/Marc.Shapiro/papers/2011/CRDTs_SSS-2011.pdf ；https://link.springer.com/chapter/10.1007/978-3-642-24550-3_29 | [13]；有条件收敛及正确论文集名称 |
| MIT 保存的 Chord 原文 | https://pdos.csail.mit.edu/papers/chord:sigcomm01/chord_sigcomm.pdf | [14]；环、指位表、查找和动态节点 |
| Birman / Joseph 原文及作者项目书目 | https://pages.cs.wisc.edu/~remzi/Classes/739/Papers/p47-birman.pdf ；https://www.cs.cornell.edu/Info/Projects/ISIS/ISISpapers.html | [15]；可靠组通信与交付顺序 |
| Crossref 官方接口 | https://api.crossref.org/works/10.1145/358527.358537 ；https://api.crossref.org/works/10.1145/1435417.1435432 ；https://api.crossref.org/works/10.1007/978-3-642-24550-3_29 | 出版方登记书目交叉核对；不替代技术原文 |

重要修正：Gray 文末提及早期三阶段协议，但不是本报告现代 3PC 非阻塞模型的主要依据；检查点结合日志回放应归为后向恢复。网络访问中的失败/限流没有记作成功验证，相关替代原文路径见核验表。
