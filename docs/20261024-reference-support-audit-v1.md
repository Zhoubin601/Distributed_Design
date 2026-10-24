# 15 条参考文献的实质核验与 v4 修订

核验及实际访问日期：2026-10-24。依据用户本轮授权，实际访问官网、原作者页面、论文原件、出版方及元数据接口，结合 raw 中本地教材与课件核对。被审查源稿为 `output/v3/20261024-misttable-distributed-design-v3.docx`。

## 结论

15 条文献均找到对应的原始材料或权威书目信息；与正文相关的核心概念有来源支持。**但 v3 并非只缺一个访问日期：还发现页码、会议名称、引用归属和恢复术语方面的问题。** 已据此制作独立 v4，保持原章节、团队资料及总体设计。

本次核验区分：文献直接定义或论证的内容；从理论推演的本项目设计；未经实现验证的工程效果。来源支持基本概念，不等于证明本系统的权限隔离、fencing、快照衔接或性能已经实现。

## 逐条核验矩阵

下列网络链接均于 2026-10-24 实际访问；本地资料同日引用。页码优先使用论文印刷页；标为“物理页”的是 PDF 页序。

| 编号 | 正文位置及用途 | 核实的原始依据与位置 | 结论及处理 |
|---|---|---|---|
| [1] 宋杰修改课件 | 第 1–8 章理论框架；同步、一致性、容错等 | `raw/Introduction to Distributed System-by JieSong NEU.pdf`，共 502 页；物理页 4、155、261、321、346–350、370、498–501 等 | 支持对应课程概念和算法比较。2014 是页脚修改年，不能改写为课程当前开课年。 |
| [2] Tanenbaum / Van Steen 教材 | 分布式系统定义、进程、命名、顺序一致性和恢复 | `raw/00-Distributed System-Principle and Paradigms (2nd Edition).pdf`；定义物理页 20，顺序一致性物理页 299–300，3PC 印刷页 361–363，恢复印刷页 363–365 | 支持基本模型。检查点加日志回放属于后向恢复，v3 的“前向恢复”术语需修正；UUIDv4 的具体选型与数据库约束明确为本项目设计。 |
| [3] Lamport 1978 | 第 6 章逻辑时钟和因果先行 | [原作者提供的论文](https://lamport.azurewebsites.net/pubs/time-clocks.pdf)，pp. 558–565，偏序关系与 Clock Condition | 支持因果先行蕴含时间戳递增，并不支持其逆命题。原文没有证明本项目 roomSeq 就是 Lamport 时钟，报告对此已区分。 |
| [4] Gifford 1979 | 第 7 章加权仲裁比较 | [论文原件，SFU 课程存档](https://www.cs.sfu.ca/~vaughan/teaching/431/papers/gifford79.pdf)，pp. 150–162，摘要及算法的读写票数、版本约束 | 支持加权读写仲裁和版本选择。等权是各副本票数为 1 的特例；集合相交不是任意故障模型下强一致性的独立充分证明，报告没有据此作保证。 |
| [5] Ricart / Agrawala 1981 | 第 6 章互斥算法及 2(N−1) 消息 | [论文原件，Illinois 课程存档](https://courses.grainger.illinois.edu/cs425/fa2023/358527.ricart-agrawala.pdf)，算法 §2.1 及故障讨论；[出版方 DOI](https://doi.org/10.1145/358527.358537) 的元数据另经 Crossref 核实 | 支持请求/应答和消息数。期刊页码为 **9–17**，v3 的 8–17 有误。将其用途写为互斥，不与时钟的因果识别用途混为一谈。 |
| [6] Mattern 1989 | 第 6 章向量时钟 | [原作者所在研究组保存的论文](https://vs.inf.ethz.ch/publ/papers/VirtTimeGlobStates.pdf)；[作者书目页](https://vs.inf.ethz.ch/publ/bibtex.html?file=papers%2FVirtTimeGlobStates)，pp. 215–226 | 支持向量时间与因果关系；其识别能力建立在论文的进程/事件模型下。补全论文集为 Workshop on Parallel and Distributed Algorithms；不把本项目标量序号当作向量时钟。 |
| [7] Fielding 2000 | 第 2 章分层 C/S；管理接口背景 | [UCI 保存的学位论文目录](https://www-test.ics.uci.edu/~fielding/pubs/dissertation/top.htm)及[第 3 章](https://www-test.ics.uci.edu/~fielding/pubs/dissertation/net_arch_styles.htm) | 支持架构风格讨论；不能证明桌游业务的具体分层和事件通知组合。v4 把理论出处与本项目组合设计分句陈述。 |
| [8] RFC 6455 | 第 4 章 WebSocket 双向通道 | [RFC Editor 原文](https://www.rfc-editor.org/rfc/rfc6455)，Abstract、§1.2、§5；作者 Fette / Melnikov，2011 | 支持 TCP 之上的双向通信，不负责 REST、数据库持久性或应用级幂等。v4 将 [8] 放在 WebSocket 的具体能力后。 |
| [9] Owlbear Rodeo | 第 1 章真实 VTT 场景参照 | [官网](https://www.owlbear.rodeo/)、[官方入门](https://docs.owlbear.rodeo/docs/getting-started/)、[Rooms](https://docs.owlbear.rodeo/docs/rooms/)、[Fog](https://docs.owlbear.rodeo/docs/fog/) | 官网主入口需要 JS，继续读取官方文档，核实浏览器、房间、地图/标记、迷雾及 Dice 扩展。补充真实访问日期 **[2026-10-24]**。不能由官网反推雾桌内部实现；受控瓦片和 viewSeq 是本项目设计。 |
| [10] Gray 1978 | 第 1 章事务边界；第 8 章 2PC | [原作者保存的原文](https://jimgray.azurewebsites.net/papers/dbos.pdf)，§5.8.3.3；[出版方页面](https://link.springer.com/chapter/10.1007/3-540-08755-9_9)及[作者书目](https://jimgray.azurewebsites.net/jimgraypublications.htm) | 支持事务、日志及 2PC。原文末尾确有对早期三阶段协议的提及，不能说完全未提 3PC；但本报告现代 3PC 非阻塞比较改由课件/教材 [1,2] 承担。[10] 精确放在 2PC 句后。补全论文集名称和 LNCS 60。 |
| [11] Chandy / Lamport 1985 | 第 8 章一致截面概念对照 | [原作者提供的论文](https://lamport.azurewebsites.net/pubs/chandy.pdf)，pp. 63–75，算法与通道状态 | 支持全局快照概念，不直接证明本项目权威库快照协议。报告已经明确只作对照，不声称实现 Chandy–Lamport 算法，保留该限定。 |
| [12] Vogels 2009 | 第 7 章最终/会话一致性、水位防回退 | [期刊原件，CMU 课程存档](https://15799.courses.cs.cmu.edu/fall2013/static/papers/p40-vogels.pdf)，pp. 40–44，尤其 pp. 42、44；[作者公开修订文本](https://www.allthingsdistributed.com/2008/12/eventually_consistent.html)交叉核对 | 支持读自身写、单调读、异步主备回退及用版本拒绝旧读取。期刊版明确为 2009、52(1):40–44，与 2008 Queue/博客版本区分；并非仅凭题名推断支持。 |
| [13] Shapiro 等 2011 | 第 2 章 CRDT 方案比较 | [原作者论文](https://perso.lip6.fr/Marc.Shapiro/papers/2011/CRDTs_SSS-2011.pdf)及[Springer 论文页](https://link.springer.com/chapter/10.1007/978-3-642-24550-3_29)，SSS 2011，LNCS 6976，pp. 386–400 | 支持满足相应条件的数据类型收敛，不能推出所有 P2P 都必须使用 CRDT，也不能证明防作弊和访问控制。更正论文集名称；表 2-1 收窄原有强断言。 |
| [14] Stoica 等 2001 | 第 5 章 Chord/指位表 | [MIT 保存的原论文](https://pdos.csail.mit.edu/papers/chord:sigcomm01/chord_sigcomm.pdf)，§4 查找和 finger table、§5 动态节点 | 支持去中心化查找与环/指位表机制。小规模受控房间不采用 Chord 是本项目成本权衡，未冒充论文的普遍结论。原书目信息保留。 |
| [15] Birman / Joseph 1987 | 第 4、8 章可靠组通信对照 | [论文原件，Wisconsin 课程存档](https://pages.cs.wisc.edu/~remzi/Classes/739/Papers/p47-birman.pdf)，pp. 47–76，摘要、GBCAST/ABCAST/CBCAST；[Cornell 作者项目书目](https://www.cs.cornell.edu/Info/Projects/ISIS/ISISpapers.html) | 支持故障下组通信与事件交付顺序。虚拟同步模型主要引用课件，不把本系统的不同授权视图流当作原文协议；v4 将引用放到可靠组通信句旁。 |

## 实际修改

共 14 处定点修订，逐项新旧全文保存在 `docs/20261024-reference-audit-v1/change-manifest.json`，包括：

- [9] 补实际访问日期；[5] 修正页码；[6] 补全论文集；[10] 补全论文集及卷号；[13] 更正论文集及卷号。
- 分开“分层架构的出处”和“本项目事件通知组合”；把 RFC 引用限定在 WebSocket 能力。
- 命名原则与 UUIDv4 具体选型分开，补权威库唯一约束；没有给理论课件强加 UUIDv4 标准的出处。
- 区分逻辑时钟、向量时钟和互斥的用途；区分文献故障模型与本项目 fencing 方案。
- 把 [10] 精确用于 2PC，把 3PC 比较交由 [1,2]；不据此承诺任意网络分区下非阻塞。
- 将“检查点加日志回放用于前向恢复”改为后向恢复；把 [15] 的支持范围限定在可靠组通信。
- 表 2-1 不再声称 P2P 必须使用共识或 CRDT，而要求另行设计定序与合并。

没有增删一级、二级标题，没有改团队表、附录填写、功能范围和性能数值。参考文献保持 15 条。

## 核验方法与限制

逐条核对的是**本报告实际引用的概念和结论**，不代表为每篇论文做完整审稿或为所有算法重做证明。先提取 v3 所有引用段落及含引用表格单元格，再对照来源内容；提取结果为 `v3-citation-contexts.json`。期刊 [5]、[12] 与论文集 [13] 的书目另通过 Crossref 官方 API 得到出版方提交的标题、页码及年份；[4] 的 API 请求返回限流，改以原论文核对，未将请求失败当作验证成功。

ACM 部分页面返回 403，UCI 和部分作者 PDF 存在间歇超时，因此采用同一篇原文的作者版或高校课程保存的期刊原件，并以出版方/作者书目交叉核对，没有用博客摘要替代已经取得的期刊原文。Owlbear 网站著录不添加没有依据的发表年份。

本项目的房间单权威、视图序号、授权瓦片、日志分发、任期隔离和性能目标仍属于设计推演。文献提供理论依据，不作为这些机制已经通过代码、压测或故障注入的证明。不能替成员证明其本人此前实际阅读过这些文献；成员应据本核验表熟悉所引用内容。

## 文件与验收

正式交付文件位于：

- `output/v4/20261024-misttable-distributed-design-v4.docx`
- `output/v4/20261024-misttable-distributed-design-v4.pdf`

过程目录为 `docs/20261024-reference-audit-v1/`；生成脚本为 `docs/scripts/build_report_v4_references.py`，独立核验脚本为 `docs/scripts/verify_report_v4_references.py`。使用现有 Word 原生字段刷新及 PDF 导出脚本，检查目录、页码、正文表格和页面图像。最终校验结果以同目录日志及 `final-verification.json` 为准。

原 raw、v3 Word/PDF 保留。本轮不重新设计章节，也不生成未经核验的正式文件。可用技能为 officecli-docx 与 pdf；项目指定 minimax 系列当前不可用，使用先前已说明的替代流程。

### 最终验收结果

21 项 pytest、33 项结构/引用/分页验收及 20 项独立核对全部通过，OfficeCLI OpenXML 校验通过。最终 Word 原生目录与 PDF 一致，共 26 页；15 条参考文献字体统一为 9 pt，修订段落的引用仍为上标。已浏览最终全部页面联系表，并放大检查参考文献页，未发现新截断或表格缺行。正式目录只复制通过验证的 Word/PDF，文件 SHA-256 与过程目录一致；原 raw 和 v3 校验值保持不变。
