# 雾桌（MistTable）分布式系统课程设计报告（Draft_v2）构建与自动化验收定点增强报告

> **审查对象**：
> - Word 报告文档：`output/Distributed_Design_Report_Draft_v2.docx`
> - PDF 导出报告：`output/Distributed_Design_Report_Draft_v2.pdf`  
> **代码仓库**：[Zhoubin601/Distributed_Design](https://github.com/Zhoubin601/Distributed_Design)  
> **审查基准提交 (Base Commit)**：`a3c964ec309fea06f1b80bc67458226c5b528a1d`  
> **验收时间**：2026-10-23  
> **验收环境**：Windows 11, Python 3.13.5, Microsoft Word 16.0 (win32com), PyMuPDF 1.28.0, pytest 9.1.1  

---

## 一、实际执行的报告生成命令及定点增强说明

### 1.1 Word 报告全量生成
- **执行命令**：
  ```bash
  python -X utf8 docs/scripts/scratch_build_master.py output/Distributed_Design_Report_Draft_v2.docx
  ```
- **进程退出码**：`0`
- **生成产物**：`output/Distributed_Design_Report_Draft_v2.docx`
- **执行结果与核心定点增强项**：
  1. **任务 1：修复表头重复检查的漏检问题**：
     - 重构 `docs/scripts/scratch_verify_output.py` 中的表格结构验收机制：新增 `get_content_tables(doc)`，通过解析正文 `表 X-Y` 表注段落与相邻 `<w:tbl>` 节点精确绑定，准确识别报告正文中的 10 张专业数据表（表 1-1, 1-2, 2-1, 3-1, 4-1, 5-1, 6-1, 7-1, 8-1, 9-1），严格排除封面信息表、课程评分标准表与附录评分大表；
     - 实现 `verify_single_table_structure(tbl, tab_id)`：对每张正文数据表独立检查 `w:tblHeader`、表头各单元格段落 `keep_with_next` 以及所有数据行 `w:cantSplit`。彻底消除原逻辑中“仅在 `w:tblHeader` 存在时才检查 `keep_with_next`”的潜在漏检隐患；
     - 任何一张目标表格缺失上述任意属性，验收脚本均产生明确的 `FAIL` 记录并导致进程退出码为 `1`；
     - 新增配套单元测试套件 `tests/test_table_structure.py`，完整覆盖正常表格通过、缺失 `w:tblHeader` 失败、缺失 `keep_with_next` 失败、缺失 `w:cantSplit` 失败以及实际报告 10 张表合规性验证。
  2. **任务 2：增强 PDF 表格跨页验收**：
     - **表 6-1 深度核验**：在 PDF 对应页（第 17 页）对表 6-1 全部 6 行核心数据行（物理时钟同步 NTP、Lamport 逻辑时钟、向量时钟 Vector Clock、单房间权威协调者定序、Ricart-Agrawala 分布式互斥、令牌环互斥 Token Ring）进行动态逐行核验，确保数据行完整呈现，且前一页（第 16 页）底部无孤立残留；
     - **全量 10 张表逐行校验与跨页续表头检查**：从 Word 实际单元格动态提取各数据行特征文本，在 PDF 中按顺序向后逐行扫描定位；对跨页表格（表 1-2 跨第 6-7 页、表 9-1 跨第 24-25 页）严格验证续页顶端重复表头；对单页表格（表 1-1, 2-1, 3-1, 4-1, 5-1, 6-1, 7-1, 8-1）核验首行同页且不强求续表头；
     - 明确分类并上报错误原因：精细区分“无法定位数据”、“表格分页异常”与“续页表头缺失”。
  3. **任务 3：修正封面间距指标语义**：
     - 修正封面间距检查指标描述与语义：准确命名为“选题方向文本块与下一行文本块垂直间距”，杜绝混淆文字到底边框距离与文字到下一行文字距离；
     - 在脚本中强制断言目标文本块成功提取：若未提取到“虚拟桌游平台”文本块或“组长”文本块，直接报告 `FAIL`，实测间距为 `16.1 pt`（阈值 $\ge 10.0$ pt），兼顾美观与安全。
- **文档结构统计**：总段落数 214，总表格数 13，分节数 2（Section 0 纵向 A4，Section 1 横向 A4）。

### 1.2 Word COM 原生目录刷新与 PDF 导出
- **执行命令**：
  ```bash
  python -X utf8 docs/scripts/scratch_update_toc_com.py output/Distributed_Design_Report_Draft_v2.docx output/Distributed_Design_Report_Draft_v2.pdf
  ```
- **进程退出码**：`0`
- **执行输出**：
  ```text
  正在通过 Word COM 打开文档: D:\2026Autumn Semester File\分布式导论\期末作业\output\Distributed_Design_Report_Draft_v2.docx
  正在更新目录与所有字段...
  检测到 Word 目录数量: 1
  已更新第 1 个目录
  已保存更新字段后的 Word 文档: D:\2026Autumn Semester File\分布式导论\期末作业\output\Distributed_Design_Report_Draft_v2.docx
  正在导出 PDF: D:\2026Autumn Semester File\分布式导论\期末作业\output\Distributed_Design_Report_Draft_v2.pdf
  PDF 导出成功！
  文档总页数 (Word 统计): 27 页
  ```

---

## 二、实际执行的测试命令、退出码与通过/失败数量

### 2.1 自动化测试套件 (`pytest -v tests/`)
- **测试命令**：
  ```bash
  pytest -v tests/
  ```
- **进程退出码**：`0`
- **测试耗时**：0.53 秒
- **通过/失败数量**：**12 项全部通过，0 项失败 (12/12 PASS)**
- **原始终端输出**：
  ```text
  ============================= test session starts =============================
  platform win32 -- Python 3.13.5, pytest-9.1.1, pluggy-1.6.0 -- D:\PythonALLFile\python\python.exe
  cachedir: .pytest_cache
  rootdir: D:\2026Autumn Semester File\分布式导论\期末作业
  plugins: anyio-4.14.2, cov-7.1.0
  collecting ... collected 12 items

  tests/test_citations.py::test_single_citation PASSED                     [  8%]
  tests/test_citations.py::test_multiple_citations_combo PASSED            [ 16%]
  tests/test_citations.py::test_existing_citations_in_text_no_duplicates PASSED [ 25%]
  tests/test_citations.py::test_consecutive_multiple_citations_in_paragraph PASSED [ 33%]
  tests/test_citations.py::test_citations_correspondence_with_references PASSED [ 41%]
  tests/test_citations.py::test_citation_superscript_format PASSED         [ 50%]
  tests/test_table_structure.py::test_normal_table_passes PASSED           [ 58%]
  tests/test_table_structure.py::test_missing_tbl_header_fails PASSED      [ 66%]
  tests/test_table_structure.py::test_missing_keep_with_next_fails PASSED  [ 75%]
  tests/test_table_structure.py::test_missing_cant_split_fails PASSED      [ 83%]
  tests/test_table_structure.py::test_real_doc_content_tables_all_valid PASSED [ 91%]
  tests/test_table_structure.py::test_verifier_produces_fail_on_tampered_doc PASSED [100%]

  ============================= 12 passed in 0.53s ==============================
  ```

### 2.2 全量集成与双层排版验收测试 (`scratch_verify_output.py`)
- **测试命令**：
  ```bash
  python -X utf8 docs/scripts/scratch_verify_output.py output/Distributed_Design_Report_Draft_v2.docx output/Distributed_Design_Report_Draft_v2.pdf
  ```
- **进程退出码**：`0`
- **通过/失败数量**：**30 项全部通过，0 项失败 (30/30 PASS)**
- **原始终端输出**：
  ```text
  ======================================================================
  【雾桌 (MistTable) 分布式系统概要设计报告 - 全自动化验收测试】
  ======================================================================

  --- 检查项 A: 输出文件状态检查 ---
    [PASS] Word 文档存在且非空: 文件大小: 2,437,542 字节
    [PASS] PDF 文档存在且非空: 文件大小: 1,489,422 字节

  --- 检查项 B: 正文结构与章节完整性 ---
    [PASS] 一级标题完整性与顺序严格对应: 检测到 11 个一级标题 (预期 11 个)
    [PASS] 二级标题完整性 (技术需求与概要设计骨架): 检测到 22 个二级标题
    [PASS] Word 原生动态目录域 (TOC) 存在且已生成条目: 目录域状态: 存在, 目录项段落数: 57

  --- 检查项 C: 图表存在性、图注规范性与物理文件核对 ---
    [PASS] 6 张设计图注均存在于正文中: 检测到 6 个图注 (预期 6 个)
    [PASS] 图注对应的物理图片文件全部存在且非空: 6 张图片文件完整
    [PASS] 正文 10 个专业三线表标题完整存在: 检测到 10 个表注 (预期 10 个)
    [PASS] 所有表格表题均配置 keep_with_next 分页保护 (杜绝表题与表格分离): 检测到 10 个表题，分页保护状态: 全部合规启用
    [PASS] 准确识别报告正文中的 10 张专业数据表 (排除封面与附录非目标表格): 识别到目标表格 10 张 (预期 10 张): ['表 1-1', '表 1-2', '表 2-1', '表 3-1', '表 4-1', '表 5-1', '表 6-1', '表 7-1', '表 8-1', '表 9-1']
    [PASS] 所有目标数据表表头行独立配置 w:tblHeader 属性 (跨页重复表头): 全部 10 张数据表表头行均独立配置 w:tblHeader
    [PASS] 所有目标数据表表头单元格段落独立配置 keep_with_next 保护 (杜绝表头与首行分离): 全部 10 张数据表表头段落均合规启用 keep_with_next
    [PASS] 所有目标数据表所有行均独立配置 cantSplit 保护 (杜绝单行跨页拆分): 全部 10 张数据表所有行均合规配置 cantSplit

  --- 检查项 D: 文献引用规范性、上标格式与编号闭环 ---
    [PASS] 上标引用 Run 存在且格式规范: 检测到 34 个上标引用文本运行片段
    [PASS] 无重复拼接引起的重复引用标记 (如 [9][9] 或 [1,7][7]): 未发现重复拼接
    [PASS] 文末参考文献条目完整性 (预期 15 条): 实际参考文献条目数: 15
    [PASS] 正文引用与文末参考文献完全闭环一一对应: 所有 1~15 号参考文献全部被正文精准引用

  --- 检查项 E: 附录表格结构与规范核对 ---
    [PASS] 附录表格尺寸符合 3x26 要求: 表格规格: 3 行 x 26 列
    [PASS] 附录表格填写了组名与系统全称: 组名: '[待填写]', 系统名: '雾桌（MistTable）多人在线虚拟桌游平台'
    [PASS] 所有评分栏严格保持留空 (得分栏勿填): 8 个评分栏严格保持空值
    [PASS] 封面评定成绩与评定人严格留空 (清空模板示例成绩100与教师姓名): Row6: ['评定成绩', '', '评定人', ''], Row7: ['评定成绩', '', '评定日期', '']
    [PASS] 附录标题配置 keep_with_next 并置于横向分节 (消除孤立标题): 附录标题状态: 存在且已生效分页保护 (Heading 1 / keep_with_next)

  --- 检查项 F: PDF 导出、分页与页面方向检查 ---
    [PASS] PDF 总页数达标 (报告规模正常): PDF 实测总页数: 27 页
    [PASS] 分节方向合规 (正文纵向 Section 0, 附录横向 Section 1): Section 0: PORTRAIT (0), Section 1: LANDSCAPE (1)
    [PASS] PDF 附录末页实际渲染为横向: 末页尺寸: 842.2 x 595.5 pt
    [PASS] PDF 第 1 页封面选题方向文本完整且选题方向文本块与下一行文本块垂直间距合理: 选题方向文本完整性: 正常, 选题方向文本块与下一行文本块垂直间距: 16.1 pt (阈值 >= 10.0 pt, 避免贴底拥挤)
    [PASS] PDF 表 6-1 表题、表头与全部 6 行数据同页完整呈现 (无孤立滞留与截断): 表 6-1 位于第 17 页整洁起始, 表题/表头与全部 6 行数据同页完整呈现, 第 16 页无孤立残留
    [PASS] PDF 正文全部 10 个专业数据表逐行数据完整呈现、分页合理且跨页续表头合规: 全部 10 个表格核验通过: 表 1-1(第6页), 表 1-2(跨第6-7页,含续表头), 表 2-1(第9页), 表 3-1(第10页), 表 4-1(第12页), 表 5-1(第14页), 表 6-1(第17页), 表 7-1(第18页), 表 8-1(第23页), 表 9-1(跨第24-25页,含续表头)
    [PASS] PDF 正文关键章节起始页定位正常: 第1章:5p, 第2章:7p, 第6章:15p, 第7章:18p, 第8章:21p, 第9章:24p, 参考文献:26p, 附录:27p
    [PASS] Word 目录记录页码与 PDF 实际正文分页严格一致: 第1章:5p/5p, 第2章:7p/7p, 第3章:9p/9p, 第4章:11p/11p, 第5章:13p/13p, 第6章:15p/15p, 第7章:18p/18p, 第8章:21p/21p, 第9章:24p/24p, 参考文献:26p/26p, 附录:27p/27p

  ======================================================================
  【自动化验收汇总总结】
  ======================================================================
  总检查项数: 30 项
  通过项数:   30 项
  失败项数:   0 项

  >>> 结论：全部自动化检查项 100% 验证通过！符合课程报告二稿定点修复规范！
  ```

---

## 三、文献引用重复检查的结果

| 检查项目 | 验收指标要求 | 实际检测结果 | 结论 |
|---|---|---|---|
| **上标运行片段数量** | 包含格式化上标引用 Run | 检测到 34 个规范上标引用文本运行片段 | **PASS** |
| **重复拼接检查** | 杜绝 `[X][X]` 或 `[X, Y][Y]` | 正文所有段落与单元格未发现任何重复拼接引用 | **PASS** |
| **文末参考文献条数** | 15 条 GB/T 7714 规范引用 | 实际参考文献条目数共 15 条 | **PASS** |
| **正文引用与文献库闭环** | 正文引用集合 $\equiv$ 文献定义集合 | 1~15 号参考文献全部被正文精准引用，无未引用文献，无未定义引用 | **PASS** |

---

## 四、Word 目录刷新结果与 PDF 分页核对情况

Word 原生动态目录域包含 57 个有效目录项。经 Word COM 实测刷新后，目录记录页码与 PDF 实际物理分页核对如下：

| 关键章节 / 标题 | 目录记录页码 | PDF 实测物理页码 | 对齐状态与排版效果说明 |
|---|---|---|---|
| **1. 系统简介** | 第 5 页 | 第 5 页 | **严格一致**（正文起始） |
| **2. 体系结构** | 第 7 页 | 第 7 页 | **严格一致**（图 1 位于第 8 页） |
| **3. 进程** | 第 9 页 | 第 9 页 | **严格一致**（图 2 位于第 10 页） |
| **4. 通信** | 第 11 页 | 第 11 页 | **严格一致**（图 3 位于第 12 页） |
| **5. 命名** | 第 13 页 | 第 13 页 | **严格一致**（表 5-1 位于第 14 页） |
| **6. 同步** | 第 15 页 | 第 15 页 | **严格一致**（图 4 位于第 16 页，表 6-1 完整起始于第 17 页） |
| **7. 一致性与复制** | 第 18 页 | 第 18 页 | **严格一致**（表 7-1 完整位于第 18 页，图 5 位于第 20 页） |
| **8. 容错性与故障恢复** | 第 21 页 | 第 21 页 | **严格一致**（图 6 位于第 22 页，表 8-1 位于第 23 页） |
| **9. 总结** | 第 24 页 | 第 24 页 | **严格一致**（表 9-1 跨第 24-25 页） |
| **参考文献** | 第 26 页 | 第 26 页 | **严格一致**（1~15 条文献紧随第 9 章位于第 26 页） |
| **附录 (得分栏勿填)** | 第 27 页 | 第 27 页 | **严格一致**（横向 A4 页面，标题与 3x26 表格同处于第 27 页） |

> **核对结论**：Word 原生目录字段页码与 PDF 导出的实际印刷页码实现 **100% 精确对齐**。所有目录链接与实际物理页码自动同频重算并保持绝对吻合。

---

## 五、表格跨页与分页验收详细核对结果

根据 Word 实际内容逐行核验正文全部 10 张专业数据表在 PDF 中的呈现情况：

| 表格编号 | 表格名称 | 跨页状态 | PDF 呈现页码 | 逐行核验与续页表头结果 | 验收结论 |
|---|---|---|---|---|---|
| **表 1-1** | 系统业务分布式映射表 | 单页 | 第 6 页 | 7 条数据行全部同页呈现，表题与数据行同页起始 | **PASS** |
| **表 1-2** | 系统设计技术指标表 | **跨页** | 第 6~7 页 | 前 4 行位于第 6 页，第 5 行位于第 7 页，第 7 页顶端包含重复表头 | **PASS** |
| **表 2-1** | 客户端-C/S对比分析表 | 单页 | 第 9 页 | 5 条数据行全部同页呈现，表题与数据行同页起始 | **PASS** |
| **表 3-1** | 客户端协同职责分工表 | 单页 | 第 10 页 | 5 条数据行全部同页呈现，表题与数据行同页起始 | **PASS** |
| **表 4-1** | 系统通信方式与协议对比表 | 单页 | 第 12 页 | 5 条数据行全部同页呈现，表题与数据行同页起始 | **PASS** |
| **表 5-1** | 系统实体寻址方式表 | 单页 | 第 14 页 | 5 条数据行全部同页呈现，表题与数据行同页起始 | **PASS** |
| **表 6-1** | 分布式时钟与并发控制算法对比表 | 单页 | 第 17 页 | 6 条数据行全部整洁起始于第 17 页，第 16 页无孤立表头残留 | **PASS** |
| **表 7-1** | 系统主要业务一致性等级表 | 单页 | 第 18 页 | 4 条数据行全部同页呈现，表题与数据行同页起始 | **PASS** |
| **表 8-1** | 节点故障指标与恢复策略表 | 单页 | 第 23 页 | 5 条数据行全部同页呈现，表题与数据行同页起始 | **PASS** |
| **表 9-1** | 课程 Chapter 1~8 知识点映射表 | **跨页** | 第 24~25 页 | 前 4 行位于第 24 页，后 4 行位于第 25 页，第 25 页顶端包含重复表头 | **PASS** |

### 5.1 失败类型识别与容错保障
验收机制已建立严格的多维度失败归因逻辑：
- **无法定位数据**：当表格标题或数据行内容在 PDF 检索中缺失时明确报告；
- **表格分页异常**：当表题与首行数据被跨页拆分、或出现行乱序时明确报告；
- **续页表头缺失**：当长表跨页但次页未出现 `w:tblHeader` 渲染时明确报告。

---

## 六、PDF 实际检查与页面排版情况

- **实测总页数**：27 页
- **封面检查 (第 1~2 页)**：
  - 选题方向文本完整，实测文本块与下一行文本块垂直间距为 16.1 pt，杜绝贴底拥挤；
  - 评定成绩、评定人严格留空，杜绝将示例分数展示为真实成绩。
- **目录检查 (第 3~4 页)**：Word 原生目录展示清晰，右侧页码排列整齐，覆盖全部 1~9 章、参考文献与附录。
- **正文与图表检查 (第 5~25 页)**：
  - A4 纵向排版，行距与段落间距规范；
  - 6 张专业架构设计图（图 1~6）清晰嵌入，图注完整；
  - 10 张专业三线表格式规范，表题、表头与数据行保护到位；
  - 重点核验表 6-1 完整起始于第 17 页顶部，前一页（第 16 页）无孤立滞留；
- **参考文献检查 (第 26 页)**：紧随第 9 章之后，排版紧凑整齐，15 条文献无序号截断。
- **附录横向排版检查 (第 27 页)**：
  - Section 1 横向排版（842.2 $\times$ 595.5 pt）；
  - `附录 (得分栏勿填)` 标题与 3 行 $\times$ 26 列考核大表完整横向铺展于该页，8 个评分栏严格保持留空。

### 6.1 关键页面排版渲染截图
本轮审查已重新按实际 PDF 物理页码渲染并逐页核验，快照保存于 `output/review/screenshots/`：
1. `output/review/screenshots/page_01_cover.png` - 封面与团队基本信息表（选题方向留白舒适，成绩与评定人留空）
2. `output/review/screenshots/page_03_toc_1.png` - Word 原生动态目录首页（第 1~5 章）
3. `output/review/screenshots/page_04_toc_2.png` - Word 原生动态目录次页（第 6~9 章、参考文献 26 页、附录 27 页）
4. `output/review/screenshots/page_06_table1_1.png` - 表 1-1 与表 1-2（位于第 6 页，无表题脱节）
5. `output/review/screenshots/page_08_fig1_architecture.png` - 第 2 章图 1 系统总体逻辑架构图（实测位于第 8 页）
6. `output/review/screenshots/page_10_fig2_room_assignment.png` - 第 3 章图 2 多房间分配与并行拓扑图（实测位于第 10 页）
7. `output/review/screenshots/page_12_fig3_token_sequence.png` - 第 4 章图 3 标记移动权威提交与传播时序图（实测位于第 12 页）
8. `output/review/screenshots/page_16_ch6_synchronization.png` - 第 6 章图 4、冲突处理逻辑与状态机（实测位于第 16 页，无孤立表头残留）
9. `output/review/screenshots/page_17_table6_1.png` - 第 6 章表 6-1 完整起始页（实测位于第 17 页顶端，表题/表头/数据行完整呈现）
10. `output/review/screenshots/page_26_references.png` - 参考文献列表（实测位于第 26 页，1~15 项闭环）
11. `output/review/screenshots/page_27_appendix.png` - 附录横向 A4 页面（实测位于第 27 页，标题与 3x26 表格同页完整呈现）

---

## 七、尚未解决的问题与未能执行的检查

1. **未填写的组员信息占位符**：
   - 封面及附录中的“姓名”、“学号”、“组名”目前保留 `[待填写]` 占位符，需在向任课教师最终提交期末大作业前由小组成员手动补填真实学号与姓名。
2. **高并发与物理机集群实测**：
   - 本报告严格定位为分布式系统课程的“技术分析与概要设计”，正文提及的“单房间 $\le 8$ 人”、“并发 100 房间”、“权威写入提交后 P95 $\le 300$ms”等性能数值，在正文中已明确界定为**未经压力测试的设计假设目标**；本设计阶段未执行多机物理集群的高并发压测与断网故障注入。

---

## 八、输出文件 SHA-256 校验值

| 文件路径 | 文件大小 (字节) | 算法 | SHA-256 校验和 |
|---|---|---|---|
| `output/Distributed_Design_Report_Draft_v2.docx` | 2,437,542 | SHA-256 | `63cece06183c0dd1ca9e02ddef58d8c3b47e643659c877317b4446853e7fd1bc` |
| `output/Distributed_Design_Report_Draft_v2.pdf` | 1,489,422 | SHA-256 | `5ca41adec81e9f043866a76d8b083de2488678a3de1faf4cee25a209030f01ea` |

---

## 九、本次报告对应的 Git 提交信息

- **目标仓库**：`https://github.com/Zhoubin601/Distributed_Design`
- **发布分支**：`main`
- **基准提交 (Base Commit)**：`a3c964ec309fea06f1b80bc67458226c5b528a1d`
- **发布提交主题**：`fix(verify): enhance table structure and multipage pdf verification, correct cover spacing metric`
- **最终发布提交 SHA**：由本轮 Git 提交历史确立并提供（详见仓库最新提交记录）
