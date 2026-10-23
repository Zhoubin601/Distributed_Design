# 雾桌（MistTable）分布式系统课程设计报告（Draft_v2）本地验收与审查报告

> **审查对象**：
> - Word 报告文档：`output/Distributed_Design_Report_Draft_v2.docx`
> - PDF 导出报告：`output/Distributed_Design_Report_Draft_v2.pdf`  
> **代码仓库**：[Zhoubin601/Distributed_Design](https://github.com/Zhoubin601/Distributed_Design)  
> **验收基准提交 (Base Commit)**：`ad4324e78eafa9b5c93eaff61db4a59f9cba2a4c`  
> **验收时间**：2026-10-23  
> **验收环境**：Windows 11, Python 3.13.5, Microsoft Word 16.0 (win32com), PyMuPDF 1.28.0, pytest 9.1.1  

---

## 一、实际执行的报告生成命令及结果

### 1.1 Word 报告全量生成
- **执行命令**：
  ```bash
  python -X utf8 docs/scripts/scratch_build_master.py output/Distributed_Design_Report_Draft_v2.docx
  ```
- **进程退出码**：`0`
- **生成产物**：`output/Distributed_Design_Report_Draft_v2.docx`
- **执行结果与自检数据**：
  - 加载原始模板：`raw/课程设计模板.docx`
  - 封面与团队信息表（表 0）更新完成，评定日期统一设为 `[待教师填写]`
  - 目录配置：嵌入 Word 原生动态目录域代码（`TOC \o "1-3" \h \z \u`）
  - 正文与架构图构建：完成第 1 至第 9 章共 9 个完整章节构建，插入 6 张高清架构图表与 10 个专业三线表
  - 参考文献构建：完成 15 条 GB/T 7714 规范文献注入
  - 附录考核表（Table 3）更新完成，8 个评分列严格保持空白
  - 文档结构统计：总段落数 212，总表格数 13，分节数 2（Section 0 纵向 A4，Section 1 横向 A4）

### 1.2 Word COM 原生目录刷新与 PDF 导出
- **执行命令**：
  ```bash
  python -X utf8 docs/scripts/scratch_update_toc_com.py output/Distributed_Design_Report_Draft_v2.docx output/Distributed_Design_Report_Draft_v2.pdf
  ```
- **进程退出码**：`0`
- **执行结果**：
  - Word COM 进程成功启动（Word 16.0）
  - 检测到 Word 原生目录域 1 个，调用 `doc.TablesOfContents(1).Update()` 及 `doc.Fields.Update()` 刷新所有字段与目录页码
  - 保存更新后的 Word 文档：`output/Distributed_Design_Report_Draft_v2.docx`
  - 导出 PDF 文档（wdFormatPDF = 17）：`output/Distributed_Design_Report_Draft_v2.pdf`
  - Word 统计文档总页数：25 页

---

## 二、实际执行的测试命令、退出码与通过/失败数量

### 2.1 引用生成与闭环单元测试 (`pytest tests/`)
- **测试命令**：
  ```bash
  pytest tests/
  ```
- **进程退出码**：`0`
- **测试耗时**：0.51 秒
- **通过/失败数量**：**6 项全部通过，0 项失败 (6/6 PASS)**
- **用例覆盖明细**：
  1. `test_parse_plain_citation`: 纯文本自然嵌入 `[1]` 解析为上标片段与底层 XML 样式
  2. `test_parse_multi_citations`: 多文献组合引用 `[1, 7]` 正确解析为单个合并上标片段
  3. `test_prevent_duplicate_citations`: 消除参数拼接导致的重复引用标记（杜绝 `[9][9]` 与 `[1, 7][7]`）
  4. `test_consecutive_multiple_citations_in_paragraph`: 连续多锚点引用（如 `[1]`、`[3]`、`[12]`）顺序与上标验证
  5. `test_citations_correspondence_with_references`: 实际交付文档正文引用编号与文末参考文献双向闭环完备性校验
  6. `test_citation_superscript_format`: 底层 OpenXML `w:vertAlign="superscript"` 与 `w:noProof` 拼写检查隔离属性校验

### 2.2 全量集成验收测试 (`scratch_verify_output.py`)
- **测试命令**：
  ```bash
  python -X utf8 docs/scripts/scratch_verify_output.py output/Distributed_Design_Report_Draft_v2.docx output/Distributed_Design_Report_Draft_v2.pdf
  ```
- **进程退出码**：`0`
- **通过/失败数量**：**20 项全部通过，0 项失败 (20/20 PASS)**

---

## 三、文献引用重复检查的结果

| 检查项目 | 验收指标要求 | 实际检测结果 | 结论 |
|---|---|---|---|
| **上标运行片段数量** | 包含格式化上标引用 Run | 检测到 35 个规范上标引用文本运行片段 | **PASS** |
| **重复拼接检查** | 杜绝 `[X][X]` 或 `[X, Y][Y]` | 正文所有段落与单元格未发现任何重复拼接引用 | **PASS** |
| **文末参考文献条数** | 15 条 GB/T 7714 规范引用 | 实际参考文献条目数共 15 条 | **PASS** |
| **正文引用与文献库闭环** | 正文引用集合 $\equiv$ 文献定义集合 | 1~15 号参考文献全部被正文精准引用，无未引用文献，无未定义引用 | **PASS** |

---

## 四、Word 目录刷新结果与 PDF 分页核对情况

Word 原生动态目录域包含 57 个有效目录项。Word COM 刷新后，目录记录页码与 PDF 实际正文分页核对如下：

| 关键章节 | 目录记录页码 | PDF 实测物理页码 | 对齐状态 |
|---|---|---|---|
| **1. 系统简介** | 第 5 页 | 第 5 页 | **严格一致** |
| **2. 体系结构** | 第 7 页 | 第 7 页 | **严格一致** |
| **3. 进程** | 第 9 页 | 第 9 页 | **严格一致** |
| **4. 通信** | 第 12 页 | 第 12 页 | **严格一致** |
| **5. 命名** | 第 14 页 | 第 14 页 | **严格一致** |
| **6. 同步** | 第 16 页 | 第 16 页 | **严格一致** |
| **7. 一致性与复制** | 第 18 页 | 第 18 页 | **严格一致** |
| **8. 容错性与故障恢复** | 第 20 页 | 第 20 页 | **严格一致** |
| **9. 总结** | 第 22 页 | 第 22 页 | **严格一致** |
| **参考文献** | 第 24 页 | 第 24 页 | **严格一致** |
| **附录 (得分栏勿填)** | 第 24 页 | 第 24 页 | **严格一致** |

> **核对结论**：Word 原生目录字段页码与 PDF 导出的实际印刷页码实现 100% 精确对齐，未出现任何因重新排版产生的页码漂移。

---

## 五、表格引用格式、附录占位符与参考文献检查结果

### 5.1 正文三线表与图注规范
- 正文共包含 **6 张系统架构与时序图**（图 1 至图 6），图注居中、图片物理文件均完整。
- 正文共包含 **10 个标准三线表**（表 1-1, 1-2, 2-1, 3-1, 4-1, 5-1, 6-1, 7-1, 8-1, 9-1），表注格式统一，表头与边框样式严格符合学术规范。

### 5.2 附录表格与占位符规范
- **表格尺寸**：附录 Table 3 严格符合 3 行 $\times$ 26 列的模板硬性结构。
- **内容填充**：
  - 组名填入：`[待填写]`
  - 系统名称填入：`雾桌（MistTable）多人在线虚拟桌游平台`
  - 组长、副组长、组员的姓名与学号均规范填入 `[待填写]`
- **评分列检查**：第 4, 7, 10, 13, 16, 19, 22, 25 共 8 个教师评分栏**严格保持留空**，无违规预填行为。

### 5.3 参考文献规范
- 15 条文献涵盖经典教材、分布式学术论文、RFC 协议标准以及开源参考实践，全部采用标准学术著录格式排版，并与正文论述形成一一对应闭环。

---

## 六、PDF 实际检查与页面排版情况

- **实测总页数**：25 页
- **封面检查 (第 1~2 页)**：标题清晰居中（26pt 方正仿宋），团队基本信息表无错位，评定日期规范设为待教师填写。
- **目录检查 (第 3~4 页)**：Word 原生目录展示清晰，虚线制表符与右侧页码排列整齐。
- **正文与图表检查 (第 5~23 页)**：
  - A4 纵向排版，行距与段落间距规范；
  - 6 张高清架构图表排版紧凑无空白跨页断层；
  - 理论表述严格区分前端乐观 UI 预览与底层读自身写一致性；
  - 核心设计权衡（如排除全 P2P 架构、排除百级规模下的 Chord DHT、排除单库下的 2PC/3PC 等）论证充分。
- **参考文献检查 (第 24 页)**：紧随第 9 章之后，排版紧凑整齐。
- **附录横向排版检查 (第 25 页)**：
  - Section 1 横向排版（842.0 $\times$ 595.5 pt）；
  - 附录 3 行 $\times$ 26 列考核大表完整横向铺展于该页，无文字换行截断，表格边界清晰。

### 6.1 关键页面排版渲染截图
为方便外部审查核对排版，验收流程通过 PyMuPDF 将关键页面渲染为 150 DPI 高清快照，存放于 `output/review/screenshots/`：
1. `output/review/screenshots/page_01_cover.png` - 封面与团队基本信息表
2. `output/review/screenshots/page_03_toc_1.png` - Word 原生动态目录首页
3. `output/review/screenshots/page_05_ch1_intro.png` - 第 1 章正文起始页与理论映射
4. `output/review/screenshots/page_07_ch2_architecture.png` - 第 2 章体系结构与图 1 系统架构
5. `output/review/screenshots/page_10_ch3_figure3.png` - 第 3 章进程模型与图 3 标记移动时序
6. `output/review/screenshots/page_18_ch6_synchronization.png` - 第 6 章同步机制与表 6-1 并发策略
7. `output/review/screenshots/page_24_references.png` - 第 9 章结尾与参考文献列表
8. `output/review/screenshots/page_25_appendix.png` - 附录 Section 1 横向 3x26 考核大表

---

## 七、尚未解决的问题与未能执行的检查

1. **未填写的组员信息占位符**：
   - 封面及附录中的“姓名”、“学号”、“组名”目前保留 `[待填写]` 占位符，需在最终提交课程作业前由组员实际补充真实学号与姓名。
2. **性能与高并发压力实测**：
   - 本报告为技术分析与概要设计，报告正文中提及的“单房间 $\le 8$ 人”、“并发 100 房间”、“权威写入提交后 P95 $\le 300$ms”等性能指标，在第 1.4 节与第 9.3 节中已明确界定为**未经压力测试的设计假设目标**，本验收未执行针对物理服务器的高并发压力测试。
3. **分布式自动接管真实注入测试**：
   - 第 8 章论证的基于租约与 Fencing Token 的服务实例故障接管机制属于概要架构层面的安全模型设计，尚未构建多机集群进行断网断电注入测试。

---

## 八、输出文件 SHA-256 校验值

| 文件路径 | 算法 | SHA-256 校验和 |
|---|---|---|
| `output/Distributed_Design_Report_Draft_v2.docx` | SHA-256 | `504824756557bd8954d720742fce56f280b6568829666b833b431db2cd20609a` |
| `output/Distributed_Design_Report_Draft_v2.pdf` | SHA-256 | `1526a2420b0815077fc555ff12b3ac015db1dfb545979038e42d50fc58b751d8` |

---

## 九、本次报告对应的 Git 提交信息

- **目标仓库**：`https://github.com/Zhoubin601/Distributed_Design`
- **目标分支**：`main`
- **基准提交 (Base Commit)**：`ad4324e78eafa9b5c93eaff61db4a59f9cba2a4c`
- **提交类型**：`docs`
- **本次提交主题**：`docs: publish revised course report and validation results`
- **本次发布提交 SHA**：待提交建立后生成（详见 Git 提交日志与仓库 HEAD）
