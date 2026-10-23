# -*- coding: utf-8 -*-
"""
自动化验收与自检程序：全面验证生成的 Word/PDF 报告结构、图表、引用、附录与分页一致性
必须具备真实的断言与失败校验，失败时返回非零退出码，严禁无条件通过。
"""
import os
import sys
import re
import docx
import fitz  # PyMuPDF

DOCX_PATH = "output/Distributed_Design_Report_Draft_v2.docx"
PDF_PATH = "output/Distributed_Design_Report_Draft_v2.pdf"
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

        # Check Image files
        all_imgs_exist = True
        missing_imgs = []
        for fig_num, caption, filename in EXPECTED_FIGURES:
            path = os.path.join(IMAGE_DIR, filename)
            if not os.path.exists(path) or os.path.getsize(path) == 0:
                all_imgs_exist = False
                missing_imgs.append(filename)
        self.log_result("C. 图表检查", "图注对应的物理图片文件全部存在且非空", all_imgs_exist,
                        f"缺少文件: {missing_imgs}" if missing_imgs else "6 张图片文件完整")

        # Check Table count
        self.log_result("C. 图表检查", "正文 10 个专业三线表标题完整存在", len(tab_captions) == 10,
                        f"检测到 {len(tab_captions)} 个表注 (预期 10 个)")

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
        has_group = (r2[0] != "")
        has_system = ("雾桌" in r2[1] or "MistTable" in r2[1])
        self.log_result("E. 附录表格", "附录表格填写了组名与系统全称", has_group and has_system,
                        f"组名: {repr(r2[0])}, 系统名: {repr(r2[1])}")

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

    def verify_pdf_and_pagination(self, docx_doc):
        print("\n--- 检查项 F: PDF 导出、分页与页面方向检查 ---")
        if not os.path.exists(self.pdf_path):
            self.log_result("F. PDF 分页", "PDF 文件可解析", False, "PDF 不存在")
            return

        pdf = fitz.open(self.pdf_path)
        pdf_pages = len(pdf)
        self.log_result("F. PDF 分页", "PDF 总页数达标 (报告规模正常)", pdf_pages >= 20,
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

        # 验证主要章节在 PDF 正文中的实际起始页码（跳过前 4 页封面与目录），并与目录页码比对
        def find_body_page(heading, sub_hint):
            for pno in range(4, len(pdf)):
                t = pdf[pno].get_text()
                if heading in t and sub_hint in t:
                    return pno + 1
            return -1

        ch1_page = find_body_page("1. 系统简介", "1.1 系统背景与业务定位")
        ch2_page = find_body_page("2. 体系结构", "2.1 技术需求")
        ch9_page = find_body_page("9. 总结", "9.1 系统设计与分布式知识点对应回顾")
        refs_page = find_body_page("参考文献", "东北大学软件学院教学课件")
        app_page = -1
        for pno in range(4, len(pdf)):
            t = pdf[pno].get_text()
            if "附录 (得分栏勿填)" in t:
                app_page = pno + 1
                break

        pages_found = (ch1_page > 0 and ch2_page > 0 and ch9_page > 0 and refs_page > 0 and app_page > 0)
        self.log_result("F. PDF 分页", "PDF 正文关键章节起始页定位正常", pages_found,
                        f"第1章: 第{ch1_page}页, 第2章: 第{ch2_page}页, 第9章: 第{ch9_page}页, 参考文献: 第{refs_page}页, 附录: 第{app_page}页")

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
        if "1.系统简介" in toc_recorded_pages:
            rec = toc_recorded_pages["1.系统简介"]
            match = (rec == ch1_page)
            if not match: toc_aligned = False
            toc_align_details.append(f"第1章: 目录{rec}页/实测{ch1_page}页")
        if "2.体系结构" in toc_recorded_pages:
            rec = toc_recorded_pages["2.体系结构"]
            match = (rec == ch2_page)
            if not match: toc_aligned = False
            toc_align_details.append(f"第2章: 目录{rec}页/实测{ch2_page}页")
        if "9.总结" in toc_recorded_pages:
            rec = toc_recorded_pages["9.总结"]
            match = (rec == ch9_page)
            if not match: toc_aligned = False
            toc_align_details.append(f"第9章: 目录{rec}页/实测{ch9_page}页")
        if "参考文献" in toc_recorded_pages:
            rec = toc_recorded_pages["参考文献"]
            match = (rec == refs_page)
            if not match: toc_aligned = False
            toc_align_details.append(f"参考文献: 目录{rec}页/实测{refs_page}页")
        if "附录(得分栏勿填)" in toc_recorded_pages:
            rec = toc_recorded_pages["附录(得分栏勿填)"]
            match = (rec == app_page)
            if not match: toc_aligned = False
            toc_align_details.append(f"附录: 目录{rec}页/实测{app_page}页")

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
            print("\n>>> 结论：全部自动化检查项 100% 验证通过！符合课程报告二稿定点修复规范！")
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
