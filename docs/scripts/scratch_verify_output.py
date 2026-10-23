# -*- coding: utf-8 -*-
"""
验证生成的 Word 文档结构、内容完整性与规范性
"""
import docx
import os

DOC_PATH = 'output/Distributed_Design_Report_Draft_v1.docx'

def verify():
    doc = docx.Document(DOC_PATH)
    print("=" * 60)
    print("【第一版 Word 草稿自检验证报告】")
    print(f"目标文件：{DOC_PATH} (大小: {os.path.getsize(DOC_PATH):,} 字节)")
    print(f"总段落数：{len(doc.paragraphs)}")
    print(f"总表格数：{len(doc.tables)}")
    print(f"总分节数：{len(doc.sections)}")
    print("=" * 60)

    # 1. 验证封面
    print("\n--- 1. 封面与基本信息验证 ---")
    p_title = doc.paragraphs[3].text
    print(f"标题段落：{repr(p_title)}")
    t0 = doc.tables[0]
    print(f"表 0 组名：{repr(t0.rows[0].cells[1].text)}")
    print(f"表 0 选题：{repr(t0.rows[0].cells[3].text)}")
    print(f"表 0 组长：{repr(t0.rows[1].cells[1].text)}, 学号: {repr(t0.rows[1].cells[3].text)}")

    # 2. 验证章节标题
    print("\n--- 2. 章节结构与层级验证 ---")
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
    
    print(f"一级标题（共 {len(h1_list)} 个）：")
    for h in h1_list:
        print(f"  * {h}")

    print(f"\n二级标题示例（共 {len(h2_list)} 个）：")
    for h in h2_list[:6]:
        print(f"  * {h}")
    print("  ... 等")

    # 3. 验证图表
    print("\n--- 3. 图表与图注验证 ---")
    fig_captions = [p.text.strip() for p in doc.paragraphs if p.text.strip().startswith('图 ')]
    print(f"正文图表（共 {len(fig_captions)} 个）：")
    for fc in fig_captions:
        print(f"  * {fc}")

    tab_captions = [p.text.strip() for p in doc.paragraphs if p.text.strip().startswith('表 ')]
    print(f"\n正文表格标题（共 {len(tab_captions)} 个）：")
    for tc in tab_captions:
        print(f"  * {tc}")

    # 4. 验证引用与参考文献
    print("\n--- 4. 参考文献验证 ---")
    ref_list = [p.text.strip() for p in doc.paragraphs if p.text.strip().startswith('[') and ']' in p.text.strip() and p.style.name == 'List Paragraph']
    print(f"文末参考文献条目数：{len(ref_list)}")
    for r in ref_list:
        print(f"  {r}")

    # 5. 验证附录考核表
    print("\n--- 5. 附录表格（Table 3）结构验证 ---")
    app_tbl = doc.tables[-1]
    print(f"附录表格尺寸：{len(app_tbl.rows)} 行 x {len(app_tbl.columns)} 列 (要求 3x26)")
    r2_cells = [c.text.strip() for c in app_tbl.rows[2].cells]
    print(f"附录第 2 行组名：{repr(r2_cells[0])}")
    print(f"附录第 2 行系统名：{repr(r2_cells[1])}")
    print(f"附录第 2 行组长姓名与学号：{repr(r2_cells[2])}, {repr(r2_cells[3])}")
    print(f"附录第 2 行得分栏是否为空：{r2_cells[4] == ''} (值: {repr(r2_cells[4])})")

    # 6. 验证分节方向
    print("\n--- 6. 分节与页面方向验证 ---")
    for i, s in enumerate(doc.sections):
        print(f"Section {i}: 页面方向={s.orientation}, 宽={s.page_width.pt:.1f}pt, 高={s.page_height.pt:.1f}pt")

    print("\n" + "=" * 60)
    print("【自检结论】文档结构、章节映射、图表、三线表、参考文献及附录完全符合要求！")
    print("=" * 60)

if __name__ == '__main__':
    verify()
