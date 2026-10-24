# -*- coding: utf-8 -*-
"""
自动化验收与自检程序：全面验证生成的 Word/PDF 报告结构、图表、引用、附录与分页一致性
必须具备真实的断言与失败校验，失败时返回非零退出码，严禁无条件通过。
"""
import os
import sys
import re
import docx
from docx.oxml.ns import qn
import fitz  # PyMuPDF
from report_paths import resolve_report_docx, resolve_report_pdf

DOCX_PATH = resolve_report_docx()
PDF_PATH = resolve_report_pdf()
IMAGE_DIR = "assets/diagrams/images"

EXPECTED_H1 = [
    "1. 系统简介",
    "2. 体系结构",
    "3. 进程",
    "4. 通信",
    "5. 命名",
    "6. 同步",
    "7. 一致性与复制",
    "8. 容错性与故障恢复",
    "9. 总结",
    "参考文献",
    "附录 (得分栏勿填)"
]

EXPECTED_FIGURES = [
    ("1", "系统总体逻辑架构图", "fig1_logical_architecture.png"),
    ("2", "多房间分配与并行处理拓扑图", "fig2_room_assignment.png"),
    ("3", "移动标记的权威提交与状态传播时序图", "fig3_token_operation_sequence.png"),
    ("4", "同一标记并发移动冲突与版本处理流程图", "fig4_concurrent_token_moves.png"),
    ("5", "战争迷雾与角色权限状态投影图", "fig5_permission_projection.png"),
    ("6", "客户端断线重连与授权状态恢复流程图", "fig6_client_reconnect.png")
]

EXPECTED_TABLE_CAPTIONS = [
    "1-1", "1-2", "2-1", "3-1", "4-1", "5-1", "6-1", "7-1", "8-1", "9-1"
]

def get_content_tables(doc):
    """
    准确识别正文 10 个专业数据表，排除封面表、评分表、附录表等非目标表格。
    返回列表: [(tab_id, caption, table), ...]
    """
    content_tables = []
    for p in doc.paragraphs:
        m = re.match(r'^表\s*(\d+-\d+)\s*(.*)', p.text.strip())
        if m:
            tid, cap = m.group(1), m.group(2).strip()
            nxt = p._p.getnext()
            while nxt is not None and nxt.tag != qn('w:tbl'):
                nxt = nxt.getnext()
            if nxt is not None:
                for t in doc.tables:
                    if t._tbl == nxt:
                        content_tables.append((tid, cap, t))
                        break
    return content_tables

def verify_single_table_structure(tbl, tab_id=""):
    """
    独立验证单张表格的结构属性（不依赖彼此状态，杜绝漏检）：
    1. tblHeader: 表头行 (row 0) 是否包含 w:tblHeader
    2. keep_with_next: 表头单元格内的所有段落是否设置了 keep_with_next (不论 tblHeader 存在与否均严格检查)
    3. cantSplit: 表格所有行（特别是数据行）是否配置了 w:cantSplit
    返回: dict(
        has_tbl_header=bool,
        all_header_p_keep=bool,
        all_rows_cant_split=bool,
        missing_header_p_cells=list,
        missing_cant_split_rows=list,
        is_valid=bool
    )
    """
    has_tbl_header = False
    if len(tbl.rows) > 0:
        hdr_tr = tbl.rows[0]._tr
        trPr = hdr_tr.trPr
        if trPr is not None and trPr.find(qn('w:tblHeader')) is not None:
            has_tbl_header = True

    all_header_p_keep = True
    missing_header_p_cells = []
    if len(tbl.rows) > 0:
        for c_idx, cell in enumerate(tbl.rows[0].cells):
            for p_idx, p in enumerate(cell.paragraphs):
                pPr = p._p.get_or_add_pPr()
                has_kn = (p.paragraph_format.keep_with_next is True) or (pPr.find(qn('w:keepNext')) is not None)
                if not has_kn:
                    all_header_p_keep = False
                    missing_header_p_cells.append((c_idx, p_idx))

    all_rows_cant_split = True
    missing_cant_split_rows = []
    for r_idx, row in enumerate(tbl.rows):
        r_trPr = row._tr.trPr
        if r_trPr is None or r_trPr.find(qn('w:cantSplit')) is None:
            all_rows_cant_split = False
            missing_cant_split_rows.append(r_idx)

    is_valid = has_tbl_header and all_header_p_keep and all_rows_cant_split
    return {
        "has_tbl_header": has_tbl_header,
        "all_header_p_keep": all_header_p_keep,
        "all_rows_cant_split": all_rows_cant_split,
        "missing_header_p_cells": missing_header_p_cells,
        "missing_cant_split_rows": missing_cant_split_rows,
        "is_valid": is_valid
    }

def clean_pdf_txt(s):
    # 去除引用编号[x]、标点符号、空格与空白符，便于稳健比对
    s = re.sub(r'\[\d+(?:,\s*\d+)*\]', '', s)
    s = re.sub(r'[ \t\r\n\(\)（）/\\:\-—_，。；、\u3000]', '', s)
    return s


def has_real_value(value):
    return bool(value.strip()) and not re.search(r'待填写|待确认|TODO|必填|选填', value, re.I)


def find_body_page(pdf, heading, sub_hint=''):
    """Find an exact heading line, excluding TOC entries, at any page position."""
    target = clean_pdf_txt(heading)
    for i, page in enumerate(pdf):
        text = page.get_text()
        if any(clean_pdf_txt(line) == target for line in text.splitlines()) and sub_hint in text:
            return i+1
    return -1

class ReportVerifier:
    def __init__(self, docx_path, pdf_path):
        self.docx_path = docx_path
        self.pdf_path = pdf_path
        self.results = [] # list of (category, check_name, status, details)

    def log_result(self, category, name, passed, details=""):
        status = "PASS" if passed else "FAIL"
        self.results.append((category, name, status, details))
        flag = "[PASS]" if passed else "[FAIL]"
        print(f"  {flag} {name}: {details}")

    def verify_files(self):
        print("\n--- 检查项 A: 输出文件状态检查 ---")
        # 1. docx exists and size
        if os.path.exists(self.docx_path):
            size = os.path.getsize(self.docx_path)
            self.log_result("A. 输出文件", "Word 文档存在且非空", size > 50000, f"文件大小: {size:,} 字节")
        else:
            self.log_result("A. 输出文件", "Word 文档存在且非空", False, f"未找到文件 {self.docx_path}")

        # 2. pdf exists and size
        if os.path.exists(self.pdf_path):
            size = os.path.getsize(self.pdf_path)
            self.log_result("A. 输出文件", "PDF 文档存在且非空", size > 50000, f"文件大小: {size:,} 字节")
        else:
            self.log_result("A. 输出文件", "PDF 文档存在且非空", False, f"未找到文件 {self.pdf_path}")

    def verify_structure(self, doc):
        print("\n--- 检查项 B: 正文结构与章节完整性 ---")
        h1_list = []
        h2_list = []
        h3_list = []
        for p in doc.paragraphs:
            if p.style.name == 'Heading 1':
                h1_list.append(p.text.strip())
            elif p.style.name == 'Heading 2':
                h2_list.append(p.text.strip())
            elif p.style.name == 'Heading 3':
                h3_list.append(p.text.strip())

        # Check H1 list
        h1_match = (h1_list == EXPECTED_H1)
        self.log_result("B. 正文结构", "一级标题完整性与顺序严格对应", h1_match,
                        f"检测到 {len(h1_list)} 个一级标题 (预期 {len(EXPECTED_H1)} 个)")
        if not h1_match:
            print(f"      实际一级标题: {h1_list}")
            print(f"      预期一级标题: {EXPECTED_H1}")

        # Check H2 subheadings count (should have 2 per chapter 1-8, 3 in chapter 9)
        self.log_result("B. 正文结构", "二级标题完整性 (技术需求与概要设计骨架)", len(h2_list) >= 19,
                        f"检测到 {len(h2_list)} 个二级标题")

        # Check Native TOC field existence
        body = doc.element.body
        sdts = body.findall("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sdt")
        has_native_toc = False
        toc_text_count = 0
        if sdts:
            sdt = sdts[0]
            instrs = sdt.findall(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}instrText")
            for ins in instrs:
                if "TOC" in (ins.text or ""):
                    has_native_toc = True
                    break
            sdtContent = sdt.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sdtContent")
            if sdtContent is not None:
                toc_text_count = len(sdtContent.findall(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"))
        
        self.log_result("B. 正文结构", "Word 原生动态目录域 (TOC) 存在且已生成条目", has_native_toc and toc_text_count > 10,
                        f"目录域状态: {'存在' if has_native_toc else '缺失'}, 目录项段落数: {toc_text_count}")

    def verify_figures_and_tables(self, doc):
        print("\n--- 检查项 C: 图表存在性、图注规范性与物理文件核对 ---")
        fig_captions = [p.text.strip() for p in doc.paragraphs if p.text.strip().startswith('图 ')]
        tab_captions = [p.text.strip() for p in doc.paragraphs if p.text.strip().startswith('表 ')]

        # Check Figure count
        self.log_result("C. 图表检查", "6 张设计图注均存在于正文中", len(fig_captions) == 6,
                        f"检测到 {len(fig_captions)} 个图注 (预期 6 个)")

        # 检查真正嵌入交付文档的图片，不能拿素材目录中的旧图替代。
        all_imgs_exist = True
        missing_imgs = []
        for fig_num, caption, filename in EXPECTED_FIGURES:
            caps = [p for p in doc.paragraphs if p.text.startswith(f'图 {fig_num}  ')]
            embeds = caps[0]._p.getprevious().xpath('.//a:blip') if len(caps) == 1 else []
            part = doc.part.related_parts.get(embeds[0].get(qn('r:embed'))) if embeds else None
            if part is None or not part.blob:
                all_imgs_exist = False
                missing_imgs.append(filename)
        self.log_result("C. 图表检查", "六张图注均绑定非空的嵌入图片", all_imgs_exist,
                        f"缺少文件: {missing_imgs}" if missing_imgs else "6 张图片文件完整")

        # Check Table count
        self.log_result("C. 图表检查", "正文 10 个专业三线表标题完整存在", len(tab_captions) == 10,
                        f"检测到 {len(tab_captions)} 个表注 (预期 10 个)")

        # Check Table captions keep_with_next property
        all_tab_caps_keep = True
        tab_cap_paras = [p for p in doc.paragraphs if p.text.strip().startswith('表 ')]
        for p in tab_cap_paras:
            if not p.paragraph_format.keep_with_next:
                all_tab_caps_keep = False
                break
        self.log_result("C. 图表检查", "所有表格表题均配置 keep_with_next 分页保护 (杜绝表题与表格分离)", all_tab_caps_keep,
                        f"检测到 {len(tab_cap_paras)} 个表题，分页保护状态: {'全部合规启用' if all_tab_caps_keep else '存在未启用项'}")

        # 准确提取正文 10 个专业数据表（排除封面表、评分表、附录表）
        content_tables = get_content_tables(doc)
        found_target_tables = (len(content_tables) == 10)
        self.log_result("C. 图表检查", "准确识别报告正文中的 10 张专业数据表 (排除封面与附录非目标表格)", found_target_tables,
                        f"识别到目标表格 {len(content_tables)} 张 (预期 10 张): {[f'表 {t[0]}' for t in content_tables]}")

        # 独立检查每张目标数据表的 tblHeader、keep_with_next 与 cantSplit
        missing_tbl_header = []
        missing_hdr_keep = []
        missing_cant_split = []

        for tid, cap, tbl in content_tables:
            res = verify_single_table_structure(tbl, tid)
            if not res["has_tbl_header"]:
                missing_tbl_header.append(f"表 {tid}")
            if not res["all_header_p_keep"]:
                missing_hdr_keep.append(f"表 {tid} (单元格 {res['missing_header_p_cells']})")
            if not res["all_rows_cant_split"]:
                missing_cant_split.append(f"表 {tid} (行 {res['missing_cant_split_rows']})")

        self.log_result("C. 图表检查", "所有目标数据表表头行独立配置 w:tblHeader 属性 (跨页重复表头)", len(missing_tbl_header) == 0,
                        "全部 10 张数据表表头行均独立配置 w:tblHeader" if len(missing_tbl_header) == 0 else f"缺失 w:tblHeader 的表格: {missing_tbl_header}")

        self.log_result("C. 图表检查", "所有目标数据表表头单元格段落独立配置 keep_with_next 保护 (杜绝表头与首行分离)", len(missing_hdr_keep) == 0,
                        "全部 10 张数据表表头段落均合规启用 keep_with_next" if len(missing_hdr_keep) == 0 else f"存在未启用 keep_with_next 的表头: {missing_hdr_keep}")

        self.log_result("C. 图表检查", "所有目标数据表所有行均独立配置 cantSplit 保护 (杜绝单行跨页拆分)", len(missing_cant_split) == 0,
                        "全部 10 张数据表所有行均合规配置 cantSplit" if len(missing_cant_split) == 0 else f"存在未配置 cantSplit 的行: {missing_cant_split}")

    def verify_citations(self, doc):
        print("\n--- 检查项 D: 文献引用规范性、上标格式与编号闭环 ---")
        cited_numbers = set()
        duplicate_patterns = []
        superscript_count = 0

        for p_idx, p in enumerate(doc.paragraphs):
            # 统计并提取连续上标 Run (应对 Word 内部按逗号分词分片情况)
            curr_sup = ""
            for r in p.runs:
                if r.font.superscript and r.text:
                    curr_sup += r.text
                else:
                    if curr_sup:
                        superscript_count += 1
                        m = re.findall(r'\[(\d+(?:,\s*\d+)*)\]', curr_sup)
                        for match in m:
                            for n in match.split(','):
                                if n.strip().isdigit():
                                    cited_numbers.add(int(n.strip()))
                        curr_sup = ""
            if curr_sup:
                superscript_count += 1
                m = re.findall(r'\[(\d+(?:,\s*\d+)*)\]', curr_sup)
                for match in m:
                    for n in match.split(','):
                        if n.strip().isdigit():
                            cited_numbers.add(int(n.strip()))

            # 检查段落中是否存在不合规的重复拼接引用标记 (如 "[9][9]" 或 "[1, 7][7]")
            p_text = p.text
            dups = re.findall(r'(\[\d+(?:,\s*\d+)*\])\s*(\[\d+(?:,\s*\d+)*\])', p_text)
            if dups:
                duplicate_patterns.append((p_idx, dups))

        self.log_result("D. 文献引用", "上标引用 Run 存在且格式规范", superscript_count > 0,
                        f"检测到 {superscript_count} 个上标引用文本运行片段")

        self.log_result("D. 文献引用", "无重复拼接引起的重复引用标记 (如 [9][9] 或 [1,7][7])", len(duplicate_patterns) == 0,
                        f"异常重复段落: {duplicate_patterns}" if duplicate_patterns else "未发现重复拼接")

        # Check references at bottom
        ref_paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip().startswith('[') and ']' in p.text.strip() and p.style.name == 'List Paragraph']
        ref_defined = set()
        for rp in ref_paragraphs:
            m = re.match(r'^\[(\d+)\]', rp)
            if m:
                ref_defined.add(int(m.group(1)))

        self.log_result("D. 文献引用", "文末参考文献条目完整性 (预期 15 条)", len(ref_paragraphs) == 15,
                        f"实际参考文献条目数: {len(ref_paragraphs)}")

        # Check closed loop: every cited number is defined, and every defined number is cited
        cited_not_defined = cited_numbers - ref_defined
        defined_not_cited = ref_defined - cited_numbers

        closed_loop = (len(cited_not_defined) == 0 and len(defined_not_cited) == 0)
        self.log_result("D. 文献引用", "正文引用与文末参考文献完全闭环一一对应", closed_loop,
                        f"未定义引用: {cited_not_defined}, 未引用文献: {defined_not_cited}" if not closed_loop else f"所有 1~15 号参考文献全部被正文精准引用")

    def verify_appendix(self, doc):
        print("\n--- 检查项 E: 附录表格结构与规范核对 ---")
        app_tbl = None
        for tbl in doc.tables:
            if len(tbl.rows) == 3 and len(tbl.columns) == 26:
                app_tbl = tbl
                break

        if app_tbl is None:
            self.log_result("E. 附录表格", "附录表格尺寸符合 3x26 要求", False, "未找到 3 行 x 26 列的附录 Table 3")
            return

        self.log_result("E. 附录表格", "附录表格尺寸符合 3x26 要求", True, f"表格规格: 3 行 x 26 列")

        # Verify Row 2 contents
        r2 = [c.text.strip() for c in app_tbl.rows[2].cells]
        has_group = has_real_value(r2[0])
        has_system = ("雾桌" in r2[1] or "MistTable" in r2[1])
        self.log_result("E. 附录表格", "附录表格填写了组名与系统全称", has_group and has_system,
                        f"组名: {repr(r2[0])}, 系统名: {repr(r2[1])}")
        values = [c.text for t in doc.tables for row in t.rows for c in row.cells]
        placeholders = [v for v in values if re.search(r'待填写|待确认|TODO', v, re.I)]
        self.log_result('E. 提交完整', '团队表及正文无待填写占位符',
                        not placeholders and not any(re.search(r'待填写|待确认|TODO', p.text, re.I) for p in doc.paragraphs),
                        f'未填写单元格数: {len(placeholders)}')

        # Verify all scoring columns are empty
        scoring_indices = [4, 7, 10, 13, 16, 19, 22, 25]
        score_cells_empty = True
        non_empty_scores = []
        for idx in scoring_indices:
            if r2[idx] != "":
                score_cells_empty = False
                non_empty_scores.append((idx, r2[idx]))

        self.log_result("E. 附录表格", "所有评分栏严格保持留空 (得分栏勿填)", score_cells_empty,
                        f"异常非空评分栏: {non_empty_scores}" if not score_cells_empty else "8 个评分栏严格保持空值")

        # Verify Cover table 0 rating scores and evaluator fields are cleared
        t0 = doc.tables[0]
        r6 = [c.text.strip() for c in t0.rows[6].cells]
        r7 = [c.text.strip() for c in t0.rows[7].cells]
        cover_ratings_clean = (r6[1] == "" and r6[3] == "" and r7[1] == "" and r7[3] == "")
        self.log_result("E. 封面与附录", "封面评定成绩与评定人严格留空 (清空模板示例成绩100与教师姓名)", cover_ratings_clean,
                        f"Row6: {r6}, Row7: {r7}")

        # Verify Appendix heading keep_with_next
        app_heading = None
        for p in doc.paragraphs:
            if '附录 (得分栏勿填)' in p.text:
                app_heading = p
                break
        app_keep = False
        if app_heading is not None:
            pPr = app_heading._p.get_or_add_pPr()
            has_direct_kn = (pPr.find(qn('w:keepNext')) is not None) or (app_heading.paragraph_format.keep_with_next is True)
            has_style_kn = bool(app_heading.style and app_heading.style.paragraph_format.keep_with_next)
            app_keep = has_direct_kn or has_style_kn
        self.log_result("E. 封面与附录", "附录标题配置 keep_with_next 并置于横向分节 (消除孤立标题)", app_keep,
                        f"附录标题状态: {'存在且已生效分页保护 (Heading 1 / keep_with_next)' if app_keep else '异常'}")

    def verify_pdf_and_pagination(self, docx_doc):
        print("\n--- 检查项 F: PDF 导出、分页与页面方向检查 ---")
        if not os.path.exists(self.pdf_path):
            self.log_result("F. PDF 分页", "PDF 文件可解析", False, "PDF 不存在")
            return

        pdf = fitz.open(self.pdf_path)
        pdf_pages = len(pdf)
        self.log_result("F. PDF 分页", "PDF 可解析且包含页面（课程未规定页数门槛）", pdf_pages > 0,
                        f"PDF 实测总页数: {pdf_pages} 页")

        # Verify sections orientation
        sec0 = docx_doc.sections[0]
        sec1 = docx_doc.sections[1]
        sec_ok = (sec0.orientation == docx.enum.section.WD_ORIENT.PORTRAIT and
                  sec1.orientation == docx.enum.section.WD_ORIENT.LANDSCAPE)
        self.log_result("F. PDF 分页", "分节方向合规 (正文纵向 Section 0, 附录横向 Section 1)", sec_ok,
                        f"Section 0: {sec0.orientation}, Section 1: {sec1.orientation}")

        # Check last page of PDF is landscape
        last_page = pdf[-1]
        pdf_landscape = (last_page.rect.width > last_page.rect.height)
        self.log_result("F. PDF 分页", "PDF 附录末页实际渲染为横向", pdf_landscape,
                        f"末页尺寸: {last_page.rect.width:.1f} x {last_page.rect.height:.1f} pt")

        # 验证 Page 1 封面选题方向单元格文本完整性与文本块垂直间距合理性
        page1 = pdf[0]
        p1_text = page1.get_text()
        has_topic = ("选题方向" in p1_text and "多人实时协作" in p1_text and "虚拟桌游平台" in p1_text)
        blocks = page1.get_text('blocks')
        # 选题单元格可拆成两个文本块；取 B 类标签以下、组长行以上的续行。
        topic_start = [b for b in blocks if 'B：' in b[4] or 'B:' in b[4]]
        row1_b = sorted([b for b in blocks if '组长(100%)' in b[4]], key=lambda b: b[1])
        topic_b = [b for b in blocks if '虚拟桌游平台' in b[4]
                   and topic_start and row1_b
                   and b[1] >= topic_start[0][1]-1 and b[3] < row1_b[0][1]]

        extracted_blocks = bool(topic_b and row1_b)
        gap = 0.0
        space_ok = False
        if extracted_blocks:
            gap = row1_b[0][1] - topic_b[0][3]
            space_ok = (gap >= 10.0)
            cover_detail = f"选题方向文本完整性: 正常, 选题方向文本块与下一行文本块垂直间距: {gap:.1f} pt (阈值 >= 10.0 pt, 避免贴底拥挤)"
        else:
            cover_detail = f"未能提取到封面选题方向文本块或下一行(组长行)文本块: topic_found={bool(topic_b)}, row1_found={bool(row1_b)}"

        self.log_result("F. PDF 分页", "PDF 第 1 页封面选题方向文本完整且选题方向文本块与下一行文本块垂直间距合理",
                        has_topic and extracted_blocks and space_ok,
                        cover_detail)
        self.log_result('F. 封面分页', '完整封面信息表及学院名称同在第一页',
                        all(label in p1_text for label in ['评定日期', '东北大学软件学院', '组长学号']),
                        '检查封面末行，避免残留第二页')
        dollar_pages = [i+1 for i, page in enumerate(pdf) if '$' in page.get_text()]
        self.log_result('F. 公式文本', '未泄漏 LaTeX 美元符标记', not dollar_pages,
                        f'异常页: {dollar_pages}')

        # 提取正文数据表供 PDF 分页核验
        content_tables = get_content_tables(docx_doc)

        # 验证 Table 6-1 在 PDF 中的实际分页与布局位置 (杜绝表题/表头孤立在页底，并核验全部 6 行数据)
        tab6_1_pno = -1
        target_6_1 = "表" + clean_pdf_txt("6-1")
        for pno in range(len(pdf)):
            t = pdf[pno].get_text()
            for line in t.split('\n'):
                line_c = clean_pdf_txt(line)
                if line_c.startswith(target_6_1) and ("所示" not in line_c):
                    tab6_1_pno = pno + 1
                    break
            if tab6_1_pno != -1:
                break
        
        tab6_1_page_text = pdf[tab6_1_pno - 1].get_text() if tab6_1_pno > 0 else ""
        has_caption_6_1 = "表 6-1" in tab6_1_page_text
        has_header_6_1 = ("同步 / 互斥技术机制" in tab6_1_page_text or "核心运作原理" in tab6_1_page_text)
        tab6_1_clean_text = clean_pdf_txt(tab6_1_page_text)

        # 从 Word 动态提取 Table 6-1 的全部 6 行数据并在 PDF 中核验
        tbl_6_1 = None
        for tid, cap, t in content_tables:
            if tid == "6-1":
                tbl_6_1 = t
                break

        missing_rows_6_1 = []
        if tbl_6_1 is not None and tab6_1_pno > 0:
            for r_idx in range(1, len(tbl_6_1.rows)):
                r_name = tbl_6_1.rows[r_idx].cells[0].text.strip()
                kw = clean_pdf_txt(r_name)[:8]
                if kw not in tab6_1_clean_text:
                    missing_rows_6_1.append((r_idx, r_name))
        else:
            missing_rows_6_1.append((-1, "未在 Word 中定位到表 6-1 或 PDF 中未定位到第 17 页"))

        has_all_6_rows = (len(missing_rows_6_1) == 0 and len(tbl_6_1.rows) == 7 if tbl_6_1 else False)

        # 检查目标表的实际前一页，不能依赖旧版的固定物理页码。
        p16_text = pdf[tab6_1_pno-2].get_text() if tab6_1_pno > 1 else ""
        p16_no_orphan_tab6_1 = ("表 6-1  分布式时钟" not in p16_text and "同步 / 互斥技术机制" not in p16_text)

        tab6_1_layout_ok = (tab6_1_pno > 0 and has_caption_6_1 and has_header_6_1 and has_all_6_rows and p16_no_orphan_tab6_1)
        self.log_result("F. PDF 分页", "PDF 表 6-1 表题、表头与全部 6 行数据同页完整呈现 (无孤立滞留与截断)", tab6_1_layout_ok,
                        f"表 6-1 位于第 {tab6_1_pno} 页, 表题/表头及6行完整，实际前页无孤立残留" if tab6_1_layout_ok else f"表 6-1 异常: pno={tab6_1_pno}, 表题={has_caption_6_1}, 表头={has_header_6_1}, 缺少行={missing_rows_6_1}, 前页无残留={p16_no_orphan_tab6_1}")

        # 验证正文全部 10 个专业数据表逐行数据在 PDF 中呈现、分页顺序及跨页续表头合规性
        all_tables_pass = True
        table_reports = []
        table_failures = []
        pdf_page_texts = [clean_pdf_txt(p.get_text()) for p in pdf]

        for tid, cap, tbl in content_tables:
            # 1. 定位表题起始页码
            caption_pno = -1
            for pno in range(len(pdf)):
                for line in pdf[pno].get_text().split('\n'):
                    line_c = clean_pdf_txt(line)
                    if line_c.startswith(f"表{clean_pdf_txt(tid)}") and ("所示" not in line_c):
                        caption_pno = pno + 1
                        break
                if caption_pno != -1:
                    break

            if caption_pno == -1:
                all_tables_pass = False
                table_failures.append(f"表 {tid}: 无法定位表题 (无法定位数据)")
                continue

            # 2. 提取表头特征词
            hdr_cells = [clean_pdf_txt(c.text) for c in tbl.rows[0].cells if clean_pdf_txt(c.text)]

            # 3. 逐行匹配实际数据行 (从 caption_pno 开始顺序向后扫描)
            curr_pno = caption_pno
            row_pages = []
            missing_rows = []

            for r_idx in range(1, len(tbl.rows)):
                c0 = clean_pdf_txt(tbl.rows[r_idx].cells[0].text)
                c1 = clean_pdf_txt(tbl.rows[r_idx].cells[1].text) if len(tbl.rows[r_idx].cells) > 1 else ""
                # 完整首列避免将正文的 Chapter8 字样误认作 Chapter8FaultTolerance 数据行。
                kw = c0 if c0 else c1

                found_pno = -1
                for pno in range(curr_pno - 1, len(pdf)):
                    if kw in pdf_page_texts[pno]:
                        found_pno = pno + 1
                        break

                if found_pno == -1:
                    missing_rows.append((r_idx, kw))
                else:
                    row_pages.append((r_idx, found_pno))
                    curr_pno = found_pno

            if missing_rows:
                all_tables_pass = False
                table_failures.append(f"表 {tid}: 无法定位数据 (缺失行: {missing_rows})")
                continue

            # 4. 验证分页合理性：表题必须与首行数据同页
            first_row_pno = row_pages[0][1]
            if caption_pno != first_row_pno:
                all_tables_pass = False
                table_failures.append(f"表 {tid}: 表格分页异常 (表题在第 {caption_pno} 页，首行在第 {first_row_pno} 页)")
                continue

            # 5. 跨页检查与续页表头验证
            pages_spanned = sorted(list(set([caption_pno] + [p for _, p in row_pages])))
            if len(pages_spanned) > 1:
                # 跨页表格：验证后续各页是否包含重复表头
                missing_cont_hdrs = []
                for cont_page in pages_spanned[1:]:
                    has_hdr = any(len(hc) >= 2 and hc[:6] in pdf_page_texts[cont_page - 1] for hc in hdr_cells)
                    if not has_hdr:
                        missing_cont_hdrs.append(cont_page)

                if missing_cont_hdrs:
                    all_tables_pass = False
                    table_failures.append(f"表 {tid}: 续页表头缺失 (跨页 {pages_spanned}，第 {missing_cont_hdrs} 页缺少重复表头)")
                else:
                    table_reports.append(f"表 {tid}(跨第{pages_spanned[0]}-{pages_spanned[-1]}页,含续表头)")
            else:
                table_reports.append(f"表 {tid}(第{pages_spanned[0]}页)")

        self.log_result("F. PDF 分页", "PDF 正文全部 10 个专业数据表逐行数据完整呈现、分页合理且跨页续表头合规", all_tables_pass,
                        f"全部 10 个表格核验通过: {', '.join(table_reports)}" if all_tables_pass else f"异常表格: {'; '.join(table_failures)}")

        # 精确匹配标题行以排除目录，不假定正文从第5页才开始。
        def locate(heading, sub_hint):
            return find_body_page(pdf, heading, sub_hint)

        ch1_page = locate("1. 系统简介", "1.1 系统背景与业务定位")
        ch2_page = locate("2. 体系结构", "2.1 技术需求")
        ch3_page = locate("3. 进程", "3.1 技术需求")
        ch4_page = locate("4. 通信", "4.1 技术需求")
        ch5_page = locate("5. 命名", "5.1 技术需求")
        ch6_page = locate("6. 同步", "6.1 技术需求")
        ch7_page = locate("7. 一致性与复制", "7.1 技术需求")
        ch8_page = locate("8. 容错性与故障恢复", "8.1 技术需求")
        ch9_page = locate("9. 总结", "9.1 系统设计与分布式知识点对应回顾")
        refs_page = locate("参考文献", "宋杰")
        app_page = -1
        for pno in range(len(pdf)):
            t = pdf[pno].get_text()
            if any(clean_pdf_txt(line) == clean_pdf_txt('附录 (得分栏勿填)') for line in t.splitlines()):
                app_page = pno + 1
                break

        pages_found = (ch1_page > 0 and ch2_page > 0 and ch3_page > 0 and ch4_page > 0 and ch5_page > 0 and
                       ch6_page > 0 and ch7_page > 0 and ch8_page > 0 and ch9_page > 0 and refs_page > 0 and app_page > 0)
        self.log_result("F. PDF 分页", "PDF 正文关键章节起始页定位正常", pages_found,
                        f"第1章:{ch1_page}p, 第2章:{ch2_page}p, 第6章:{ch6_page}p, 第7章:{ch7_page}p, 第8章:{ch8_page}p, 第9章:{ch9_page}p, 参考文献:{refs_page}p, 附录:{app_page}p")

        # 从 docx 原生目录域超链接提取各章节的记录页码
        toc_recorded_pages = {}
        body = docx_doc.element.body
        sdts = body.findall("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sdt")
        if sdts:
            sdtContent = sdts[0].find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sdtContent")
            if sdtContent is not None:
                for p in sdtContent.findall(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
                    hl = p.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hyperlink")
                    if hl is not None:
                        t_nodes = hl.findall(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t")
                        if len(t_nodes) >= 2:
                            title_parts = [t.text for t in t_nodes[:-1] if t.text]
                            title = "".join(title_parts).strip().replace(" ", "")
                            page_text = t_nodes[-1].text.strip()
                            if page_text.isdigit():
                                toc_recorded_pages[title] = int(page_text)

        toc_aligned = True
        toc_align_details = []
        checks_map = [
            ("1.系统简介", ch1_page, "第1章"),
            ("2.体系结构", ch2_page, "第2章"),
            ("3.进程", ch3_page, "第3章"),
            ("4.通信", ch4_page, "第4章"),
            ("5.命名", ch5_page, "第5章"),
            ("6.同步", ch6_page, "第6章"),
            ("7.一致性与复制", ch7_page, "第7章"),
            ("8.容错性与故障恢复", ch8_page, "第8章"),
            ("9.总结", ch9_page, "第9章"),
            ("参考文献", refs_page, "参考文献"),
            ("附录(得分栏勿填)", app_page, "附录")
        ]
        for key, actual_pno, label in checks_map:
            if key in toc_recorded_pages:
                rec = toc_recorded_pages[key]
                match = (rec == actual_pno)
                if not match: toc_aligned = False
                toc_align_details.append(f"{label}:{rec}p/{actual_pno}p")
            else:
                toc_aligned = False
                toc_align_details.append(f"{label}:缺失")

        self.log_result("F. PDF 分页", "Word 目录记录页码与 PDF 实际正文分页严格一致", toc_aligned,
                        ", ".join(toc_align_details) if toc_align_details else "目录页码已比对")

    def run_all(self):
        print("=" * 70)
        print("【雾桌 (MistTable) 分布式系统概要设计报告 - 全自动化验收测试】")
        print("=" * 70)
        self.verify_files()
        
        if not os.path.exists(self.docx_path):
            print("\n[CRITICAL ERROR] Word 文档缺失，无法继续执行正文检查！")
            return False

        doc = docx.Document(self.docx_path)
        self.verify_structure(doc)
        self.verify_figures_and_tables(doc)
        self.verify_citations(doc)
        self.verify_appendix(doc)
        self.verify_pdf_and_pagination(doc)

        print("\n" + "=" * 70)
        print("【自动化验收汇总总结】")
        print("=" * 70)
        
        total_checks = len(self.results)
        passed_checks = sum(1 for _, _, status, _ in self.results if status == "PASS")
        failed_checks = sum(1 for _, _, status, _ in self.results if status == "FAIL")

        print(f"总检查项数: {total_checks} 项")
        print(f"通过项数:   {passed_checks} 项")
        print(f"失败项数:   {failed_checks} 项")

        if failed_checks > 0:
            print("\n>>> 存在失败检查项，详细失败清单：")
            for cat, name, status, details in self.results:
                if status == "FAIL":
                    print(f"    - [{cat}] {name}: {details}")
            print("\n>>> 结论：验收未通过！返回非零退出码。")
            return False
        else:
            print("\n>>> 结论：全部结构、引用和分页自动检查通过；技术设计及视觉质量另行复核。")
            return True

if __name__ == '__main__':
    docx_file = sys.argv[1] if len(sys.argv) > 1 else DOCX_PATH
    pdf_file = sys.argv[2] if len(sys.argv) > 2 else PDF_PATH
    verifier = ReportVerifier(docx_file, pdf_file)
    success = verifier.run_all()
    if not success:
        sys.exit(1)
    else:
        sys.exit(0)
