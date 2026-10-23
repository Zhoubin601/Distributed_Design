# -*- coding: utf-8 -*-
"""
生成第 8 章 容错性与故障恢复、第 9 章 总结、参考文献及附录更新
"""
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.enum.text import WD_ALIGN_PARAGRAPH

from scratch_report_builder_core import (
    set_run_font, set_p_spacing, add_heading_1, add_heading_2, add_heading_3,
    add_body_p, add_figure, add_table_with_caption, insert_p
)

def build_chapter_8(doc):
    """第 8 章 容错性与故障恢复 (对应 Chapter 8 — Fault Tolerance)"""
    add_heading_1(doc, "8. 容错性与故障恢复")
    
    add_heading_2(doc, "8.1 技术需求")
    add_body_p(doc,
        "在分布式网络环境下，局部故障是不可避免的常态。容错子系统必须具备应对以下典型异常的设计考量与恢复能力："
    )
    add_body_p(doc,
        "（1）弱网抖动下的状态对齐与恢复需求：玩家在无线网络或移动网络下面临短暂断连、丢包与延迟波动。系统需要设计状态判定与补发机制，在网络连通后使客户端尽快恢复到权威视图。需要强调的是，‘网络恢复后普通规模房间在 5 秒内恢复授权状态’属于未经压力测试的设计假设目标，用于指导差分恢复策略设计，而非经过实测验证的性能承诺。"
    )
    add_body_p(doc,
        "（2）网络超时不确定性下的防重复操作与幂等需求：客户端提交掷骰或标记更新请求后，由于下行网络拥塞导致响应丢失，客户端在超时后可能发起重试。系统必须避免因网络重试导致操作被重复执行（例如重复扣减角色生命值或重复记录掷骰结果），该机制严格依赖持久化操作记录与本地事务边界。"
    )
    add_body_p(doc,
        "（3）服务实例异常退出时的状态接管与防脑裂需求：负责特定房间的协作服务实例发生异常或失联时，备用接管实例需要从权威持久化存储拉取最新状态并恢复服务。在接管过程中，必须具备防止原实例与新实例同时写入的隔离机制（Fencing），避免产生双主（Split-Brain）数据混乱。"
    )

    add_heading_2(doc, "8.2 概要设计")
    
    add_heading_3(doc, "(1) 网络超时分析与基于操作唯一标识的幂等重试机制")
    add_body_p(doc,
        "在分布式系统理论中，‘请求超时（Timeout）并不等同于操作执行失败’ [1, 2]。当客户端发起掷骰请求且未在预期时间内收到确认响应时，实际物理网络中可能存在三种不同情况："
        "① 请求报文在上传途中丢失，服务端未收到；"
        "② 服务端已成功接收并执行了本地事务提交，但在返回确认响应包时下行网络发生丢包；"
        "③ 服务端正处于高负载排队中，请求正在处理但尚未完成响应。"
    )
    add_body_p(doc,
        "针对上述网络不确定性，系统设计了基于唯一标识符（`operationId`）的幂等重试机制：客户端在构造写操作请求时附加全局唯一标识符；"
        "服务端在持久化存储中，将业务状态变更与该操作标识在同一个本地事务边界内原子提交。"
        "当客户端因超时发起重试时，强制复用相同的操作标识。服务端收到重试请求后，优先检索幂等记录："
        "若命中已提交记录，则直接返回原事务执行结果，避免重复执行掷骰或数据变更；"
        "若检测到相同标识正在被并发事务处理，则提示客户端稍后重试。"
        "该机制以服务端原子事务与幂等记录为支撑，保证了网络超时重试时的操作安全性。其生效前提在于：客户端必须生成并维护全局唯一的操作标识，服务端在原子事务中保证操作与结果记录的持久性。"
    )

    add_heading_3(doc, "(2) 客户端断线重连与增量/全量快照差分恢复流程")
    add_body_p(doc,
        "针对客户端断线重连，系统设计了差分状态恢复流程。图 6 展示了客户端断线重连与授权状态恢复的逻辑流转。"
    )

    # 嵌入图 6
    add_figure(doc, "fig6_client_reconnect.png", "6", "客户端断线重连与授权状态恢复流程图")

    add_body_p(doc,
        "结合图 6，系统对重连恢复的分支判定推导如下："
        "（1）重连发起与准入重新核验：客户端检测到底层网络连接断开后，启动指数退避重连。重新建连后发送重连信令，携带身份凭证、房间标识以及本端最后成功处理的事件序号；"
        "服务端首先重新验证该用户的房间准入与权限（防止断网期间被移出房间）；"
        "（2）差分恢复决策分流：服务端对比房间最新权威事件序号与客户端上报序号："
        "① 增量补发路径（Delta Sync，轻度落后）：若落后步数处于服务端保留的历史事件窗口内，服务端直接检索落后区间的有序增量事件列表，"
        "经当前战争迷雾视野权限过滤后，打包推回给客户端按序回放补齐画面，网络传输开销较低；"
        "② 全量快照重置路径（Snapshot Reset，长时间离线）：若客户端断线时间过长超出历史保留窗口，服务端则调用状态序列化组件生成当前时刻的授权状态基准快照（Baseline Snapshot），"
        "其原理参照经典分布式快照（Distributed Snapshot）状态截面理论 [11]。快照包含预置地图标识、当前所有可见标记及其属性，客户端接收后基于基准快照重置本地图形上下文；"
        "（3）就绪确认：无论采用增量补发还是全量快照重置，客户端完成状态同步后均向服务端发送同步就绪确认帧，重新切入正常协同状态。系统将‘恢复时间 ≤ 5秒’作为设计目标用于指导差分恢复策略设计，该指标受网络环境与快照大小制约，未经实测验证。"
    )

    # 嵌入表 8-1
    tab8_1_headers = ["典型故障场景", "根本故障成因与物理表现", "系统预期容错与自愈策略", "涉及课程理论与知识点"]
    tab8_1_rows = [
        ["客户端网络突发闪断", "无线网络信号抖动，长连接异常断开", "客户端指数退避重连；服务端保留短期会话并走增量补发或快照重置", "Chapter 4 瞬态通信缺陷；Chapter 8 崩溃恢复模型"],
        ["请求提交成功但响应丢失", "上行成功入库，下行网络拥塞引发客户端超时", "客户端复用 operationId 重试，服务端命中幂等记录直接返回原结果", "Chapter 1 事务边界；Chapter 8 RPC 幂等重试语义"],
        ["房间协作服务实例异常退出", "宿主机故障或协作进程崩溃", "路由网关检测心跳超时，备用实例从持久化存储拉取快照接管服务", "Chapter 3 进程故障；Chapter 8 进程韧性与故障切换"],
        ["实时增量事件网络丢包", "长连接链路偶发丢帧或网关队列短暂溢出", "客户端感知到 sequence 不连续，主动发起增量补发拉取请求", "Chapter 4 成组通信；Chapter 7 顺序一致性与单调性"],
        ["持久化存储短暂不可用", "主数据库触发主备切换或瞬时磁盘 I/O 阻塞", "协作层暂停该房间的新写事务，向前端返回降级重试提示", "Chapter 1 ACID 持久性边界；Chapter 7 复制一致性"]
    ]
    add_table_with_caption(doc, "8-1", "典型网络与节点故障场景及恢复策略分析表", tab8_1_headers, tab8_1_rows, [1.3, 1.7, 2.0, 1.8])

    add_heading_3(doc, "(3) 协作服务进程故障接管与恢复前提边界")
    add_body_p(doc,
        "当负责某房间的协作服务实例发生故障时，系统依靠共享持久化存储进行状态恢复与接管。在此需要阐明故障接管的安全前提与潜在风险："
        "必须防范‘假死脑裂（Split-Brain）’现象。假设服务实例 1 因网络抖动或长垃圾回收停顿与网关失去联系，网关判定其离线并将该房间的协调职责分配给备用实例 2。"
        "若实例 1 随后恢复运行并未感知到已被替代，若继续向持久化存储写入数据，将造成多主并发写冲突与数据混乱。"
        "因此，故障接管机制在理论上必须引入带有租约（Lease）与递增任期号（Epoch / Fencing Token）的存储锁与准入隔离机制 [1, 2]：持久化存储在执行写入时强制核验任期标识，"
        "新实例接管时递增任期号，旧实例携带过期任期号发起的任何写操作将被底层存储拒绝，以此降低脑裂风险。"
        "需要特别指出的是，本报告对服务实例接管与隔离机制的讨论属于概要设计层面的理论推导与安全模型约束，在工程实践中依赖严格的时钟漂移控制、心跳超时阈值设定与存储层强原子条件更新能力，属于设计目标，尚未在系统中实现完整的自动化接管测试。"
    )

    add_heading_3(doc, "(4) 课件理论分析：故障分类模型、可靠通信与 2PC/3PC 适用边界")
    add_body_p(doc,
        "对照宋杰老师课件 Chapter 8（Fault Tolerance）关于容错理论与分布式提交协议的权威论述 [1]，系统建立如下理论映射："
    )
    add_body_p(doc,
        "1. 故障模型界定（Fault Models）："
        "课件将分布式系统故障划分为崩溃故障（Crash-Stop）、崩溃恢复故障（Crash-Recovery）、省略故障（Omission Failure）、定时故障（Timing Failure）以及拜占庭故障（Byzantine Failure / Arbitrary Failure）。"
        "雾桌平台将系统容错边界明确界定在‘非拜占庭的崩溃-恢复故障与网络省略故障’范围内：假定服务端进程与数据库发生故障后会重启恢复，网络消息可能丢包或延迟，但服务端节点内部假定不存在伪造恶意数据的拜占庭叛徒行为。"
        "对于客户端可能存在的伪造请求或作弊嗅探，系统通过严格的服务端鉴权与战争迷雾差分投影加以防御，而非在系统内部引入开销巨大的拜占庭容错协议。"
    )
    add_body_p(doc,
        "2. 可靠通信与 RPC 失败语义（RPC Semantics Under Failure）："
        "课件分析了 RPC 面临节点崩溃或消息丢失时的常见语义：至少一次（At-least-once）、至多一次（At-most-once）与恰好一次（Exactly-once）。"
        "在不可靠的物理网络环境下，网络消息本身无法天然保证只投递一次。雾桌平台在网络层采用带有超时的重试机制（体现‘至少一次’通信倾向），在应用层结合唯一 `operationId` 幂等记录与事务更新，"
        "从而在端到端应用语义层面逼近‘恰好一次（Effectively-once / Idempotent Execution）’的处理效果，其本质是‘至少一次传输 + 幂等去重’，而非物理网络保证消息只投递一次。"
    )
    add_body_p(doc,
        "3. 分布式两阶段提交（2PC）与三阶段提交（3PC）适用性论证："
        "课件 Chapter 8 推导了两阶段提交（Two-Phase Commit, 2PC）与三阶段提交（3PC）在保障跨节点分布式事务原子性方面的机制与限制 [1, 10]。"
    )
    add_body_p(doc,
        "设计论证：2PC/3PC 适用于‘单个逻辑业务操作需要跨越多个独立的分布式资源管理器（如多个独立数据库或消息队列）保持原子提交’的场景。其代价是协调者单点阻塞、长时持有锁资源以及网络分区下的阻塞风险。"
        "在雾桌平台的概要设计中，我们将同一房间内的状态变更、增量事件生成与操作幂等记录，归集在‘同一个权威持久化数据库实例的本地事务’中完成。"
        "由于不涉及跨独立数据库的分布式事务参与者，底层数据库自身的预写式日志（WAL）与事务隔离机制足以保障单个房间写操作的 ACID 特性。"
        "因此，在现阶段的单数据库权威存储架构下，引入跨节点 2PC/3PC 缺乏业务必要性，属于过度设计；本设计明确界定其适用边界，仅将其作为未来数据分片或跨服务微服务拆分时的可选演进方案。"
    )

def build_chapter_9(doc):
    """第 9 章 总结"""
    add_heading_1(doc, "9. 总结")
    
    add_heading_2(doc, "9.1 系统设计与分布式知识点对应回顾")
    add_body_p(doc,
        "本报告针对选题 B‘多人实时协作的在线虚拟桌游平台’，完成了一套面向课程要求的分布式系统概要设计说明书。"
        "系统紧扣分布式系统的核心特征与工程权衡展开设计，涵盖了《分布式系统导论》课程教学大纲与宋杰老师课件中 Chapter 1 至 Chapter 8 的核心理论模块 [1]，"
        "尝试将理论概念与业务架构建立对应。课程核心知识点在系统设计中的应用与映射如表 9-1 所示。"
    )

    tab9_1_headers = ["课程课件章节", "核心概念与理论依据", "本系统概要设计中的具体映射与落地", "不采用或边界限定说明"]
    tab9_1_rows = [
        ["Chapter 1 Introduction", "分布式目标、透明性、陷阱、ACID 事务", "定义网络延迟假定；以单库本地事务为边界；透明性与迷雾隔离权衡", "不把数据库提交成功等同于网络广播送达"],
        ["Chapter 2 Architectures", "分层架构、C/S、P2P 对等网络、事件驱动", "分层客户端—服务器架构；按房间分配权威协作；事件驱动异步通知", "分析并排除全 P2P 架构（基于防作弊与迷雾要求）"],
        ["Chapter 3 Processes", "线程模型、并发处理、客户端分工、代码迁移", "瘦客户端交互、服务端权威排队；异步事件驱动思路", "论证桌游业务无需动态代码迁移，予以排除"],
        ["Chapter 4 Communication", "RPC、瞬态通信、持久通信、面向流通信", "REST 接口与全双工长连接；增量事件持久化存储记录", "明确判定长连接/广播通知为瞬态，恢复依赖持久化记录"],
        ["Chapter 5 Naming", "平面命名、结构化命名、邀请凭证、DHT/Chord", "UUIDv4 实体全局唯一（非安全授权）；邀请短码哈希；路由目录", "强调随机 ID 不能替代权限验证；百级规模排除自建 Chord"],
        ["Chapter 6 Synchronization", "物理时钟偏差、Lamport 时钟与权威定序区分、互斥算法", "单房间权威单调事件序号定序 + 乐观版本校验；Lamport 时钟阐释因果序", "明确区分理论因果序与服务端权威序号；说明 Ricart-Agrawala 2(N-1) 消息开销过大并排除"],
        ["Chapter 7 Consistency", "顺序一致性、读自身写与乐观预览区分、主备复制与 Quorum", "核心数据顺序一致；已提交写保障读自身写；前端推测预览解耦；迷雾零信任投影", "采用成熟主备异步复制候选；指明等权 Quorum (R+W>N, W>N/2) 与加权模型的区别及适用边界"],
        ["Chapter 8 Fault Tolerance", "故障模型、RPC幂等、崩溃恢复、2PC/3PC", "唯一操作标识幂等记录；差分状态恢复流程；租约防脑裂讨论", "单库事务自足，论证当前阶段为何无需引入 2PC/3PC"]
    ]
    add_table_with_caption(doc, "9-1", "课程 Chapter 1–8 知识点在系统设计中的应用与映射对应表", tab9_1_headers, tab9_1_rows, [1.3, 1.6, 2.0, 1.8])

    add_heading_2(doc, "9.2 核心设计取舍与工程理性总结")
    add_body_p(doc,
        "纵观全篇报告，本设计围绕实际业务需求与分布式系统基本原理展开推演，体现了以下设计取舍与思考："
        "（1）在体系结构选择上：基于多人在线桌游存在严格信息不对称（战争迷雾）与防作弊要求的业务特点，报告论证了全 P2P 架构在客户端作弊防范与弱网一致性上的局限，确立了分层客户端—服务器架构与单房间权威协调机制；"
        "（2）在并发控制与同步上：避免在客户端复杂堆叠分布式互斥锁或多主 CRDT 算法 [13]，采用单房间权威排队与乐观版本号校验，实现了较为简洁的冲突检测与安全回滚流程，降低了系统整体协调开销；"
        "（3）在通信与容错设计上：区分了瞬态通信通道与持久化状态记录的职责差异，认识到‘网络消息发送成功不等于客户端接收’以及‘网络请求超时不等于操作执行失败’的客观规律，结合唯一 `operationId` 幂等机制与差分状态恢复策略构建容错逻辑；"
        "（4）在安全边界防范上：确立零信任客户端原则，通过服务端差分投影机制限制未授权数据下发，有效规避了客户端内存窃取战争迷雾底层数据的作弊风险。"
    )

    add_heading_2(doc, "9.3 设计局限性与未验证假设声明")
    add_body_p(doc,
        "遵循严谨求实的科学态度，报告对本设计的局限性与待验证项作出如下客观说明："
        "（1）性能指标属于未经测试的设计假设与目标：单房间最多 8 人、初始约 100 个并发房间、P95 延迟目标 ≤ 300ms（权威库提交至授权客户端）与常规 API 处理 P95 延迟 ≤ 500ms，以及网络恢复后普通房间 5 秒内恢复状态等指标，"
        "均为用于辅助系统推演的设计假设或设计目标，不是教师规定的硬性指标，也不是已经实现或经过压力测试验证的性能承诺，实际表现受限于网络环境、硬件配置与并发争用程度；"
        "（2）异步复制下的数据丢失风险：若持久化存储采用主备异步流复制机制，在主节点发生突发硬件掉电或严重故障时，尚未复制到备用节点的数据存在丢失风险，系统不承诺绝对的‘零数据丢失’；"
        "（3）服务接管机制尚未经过完整工程实现验证：虽然提出了租约与 Fencing Token 的防脑裂思路，但自动故障切换在实际生产中对心跳阈值、时钟漂移和网络分区的容忍度要求极高，本报告仅给出了概要设计方案，尚未完成详细工程实现与极端测试；"
        "（4）单房间权威排队与系统水平扩展的权衡：单房间由单一权威节点协调简化了并发控制，但若未来出现超大规模房间或极高频标记更新，该单点可能成为局部吞吐瓶颈，需在后续详细设计中进一步评估水平切分策略。"
        "上述局限性为系统后续的工程原型实现、性能基准测试与详细架构设计提供了明确的方向。"
    )

REFERENCES = [
    "[1] 宋杰. 分布式系统导论 (Introduction to Distributed System) [Z]. 东北大学软件学院教学课件, 2024.",
    "[2] TANENBAUM A S, VAN STEEN M. Distributed systems: principles and paradigms [M]. 2nd ed. Upper Saddle River: Pearson Prentice Hall, 2007.",
    "[3] LAMPORT L. Time, clocks, and the ordering of events in a distributed system [J]. Communications of the ACM, 1978, 21(7): 558-565.",
    "[4] GIFFORD D K. Weighted voting for replicated data [C]//Proceedings of the seventh ACM symposium on Operating systems principles. 1979: 150-162.",
    "[5] RICART G, AGRAWALA A K. An optimal algorithm for mutual exclusion in computer networks [J]. Communications of the ACM, 1981, 24(1): 8-17.",
    "[6] MATTERN F. Virtual time and global states of distributed systems [C]//Parallel and Distributed Algorithms. North-Holland, 1989: 215-226.",
    "[7] FIELDING R T. Architectural styles and the design of network-based software architectures [D]. Irvine: University of California, Irvine, 2000.",
    "[8] FETTE I, MELNIKOV A. The WebSocket Protocol [R]. RFC 6455, 2011.",
    "[9] Owlbear Rodeo. Owlbear Rodeo: A virtual tabletop for tabletop role-playing games [EB/OL]. (2020) [2026-10-23]. https://www.owlbear.rodeo.",
    "[10] GRAY J. Notes on data base operating systems [M]//Operating Systems. Berlin: Springer, 1978: 393-481.",
    "[11] CHANDY K M, LAMPORT L. Distributed snapshots: determining global states of distributed systems [J]. ACM Transactions on Computer Systems, 1985, 3(1): 63-75.",
    "[12] VOGELS W. Eventually consistent [J]. Communications of the ACM, 2009, 52(1): 40-44.",
    "[13] SHAPIRO M, PREGUIÇA N, BAQUERO C, et al. Conflict-free replicated data types [C]//Symposium on Self-Stabilizing Systems. Berlin: Springer, 2011: 386-400.",
    "[14] STOICA I, MORRIS R, KARGER D, et al. Chord: A scalable peer-to-peer lookup service for internet applications [J]. ACM SIGCOMM Computer Communication Review, 2001, 31(4): 149-160.",
    "[15] BIRMAN K P, JOSEPH T A. Reliable communication in the presence of failures [J]. ACM Transactions on Computer Systems, 1987, 5(1): 47-76."
]

def build_references(doc):
    """参考文献 (GB/T 7714 规范)"""
    add_heading_1(doc, "参考文献")
    
    for ref in REFERENCES:
        p = insert_p(doc, style='List Paragraph')
        set_p_spacing(p, before=24, after=24)
        pPr = p._p.get_or_add_pPr()
        ind = pPr.find(qn('w:ind'))
        if ind is None:
            ind = OxmlElement('w:ind')
            pPr.append(ind)
        ind.set(qn('w:leftChars'), '0')
        r = p.add_run(ref)
        set_run_font(r, east_asia='SimSun', size_pt=9.0)

def update_appendix_table(doc):
    """更新附录表格 (Table 3)，确保完全符合不允许修改附录的要求"""
    # 查找最后的 3x26 附录表格
    app_table = None
    for tbl in doc.tables:
        if len(tbl.rows) == 3 and len(tbl.columns) == 26:
            app_table = tbl
            break
    
    if app_table is None:
        print("未定位到附录 Table 3")
        return

    # 第 2 行数据填充
    # Row 0: 组名 | 系统名 | 组长 (x3) | 副组长1 (x3) | 副组长2 (x3) | 副组长3 (x3) | 组员1 (x3) | 组员2 (x3) | 组员3 (x3) | 组员4 (x3)
    # Row 1: 组名 | 系统名 | 姓名 | 学号 | 得分 | 姓名 | 学号 | 得分 ...
    # Row 2: 填充组名、系统名、姓名学号占位，得分留空！
    r2 = app_table.rows[2]
    r2.cells[0].text = '[待填写]'
    r2.cells[1].text = '雾桌（MistTable）多人在线虚拟桌游平台'
    
    # 组长
    r2.cells[2].text = '[待填写]'
    r2.cells[3].text = '[待填写]'
    r2.cells[4].text = '' # 得分栏勿填
    
    # 副组长 1
    r2.cells[5].text = '[待填写]'
    r2.cells[6].text = '[待填写]'
    r2.cells[7].text = ''
    
    # 副组长 2
    r2.cells[8].text = '[待填写]'
    r2.cells[9].text = '[待填写]'
    r2.cells[10].text = ''
    
    # 副组长 3
    r2.cells[11].text = '[待填写]'
    r2.cells[12].text = '[待填写]'
    r2.cells[13].text = ''
    
    # 组员 1~4
    for idx, col_start in enumerate([14, 17, 20, 23]):
        r2.cells[col_start].text = '[待填写]'
        r2.cells[col_start + 1].text = '[待填写]'
        r2.cells[col_start + 2].text = ''

    # 规范字体
    for row in app_table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for r in p.runs:
                    set_run_font(r, east_asia='SimSun', size_pt=7.5)

    print("附录考核表 (Table 3) 按照模板规范完成数据填充，得分栏保持留空")

print("Chapter 8, 9, References and Appendix builder ready.")
