# -*- coding: utf-8 -*-
"""
封面与目录管理模块（修订版：移除硬编码评定日期，支持真实目录更新）
"""
import os
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

from scratch_report_builder_core import set_run_font, set_p_spacing

def update_cover_page(doc):
    """更新封面标题与表 0 团队基本信息"""
    for p in doc.paragraphs[:10]:
        if 'XXXX系统' in p.text or '技术分析和概要设计' in p.text:
            p.text = ''
            r1 = p.add_run("雾桌（MistTable）多人在线虚拟桌游平台的\n")
            set_run_font(r1, east_asia='FangSong_GB2312', size_pt=26, bold=True)
            r2 = p.add_run("技术分析和概要设计")
            set_run_font(r2, east_asia='FangSong_GB2312', size_pt=26, bold=True)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            set_p_spacing(p, before=180, after=180)
            break

    # 更新表 0 (团队基本信息)
    t0 = doc.tables[0]
    t0.rows[0].cells[1].text = '[待填写]'
    t0.rows[0].cells[3].text = 'B：多人实时协作的在线虚拟桌游平台'
    
    t0.rows[1].cells[1].text = '[待填写]'
    t0.rows[1].cells[3].text = '[待填写]'
    t0.rows[2].cells[1].text = '[待填写]'
    t0.rows[2].cells[3].text = '[待填写]'
    t0.rows[3].cells[1].text = '[待填写]'
    t0.rows[3].cells[3].text = '[待填写]'
    t0.rows[4].cells[1].text = '[待填写]'
    t0.rows[4].cells[3].text = '[待填写]'
    t0.rows[5].cells[1].text = '[待填写（不多于4人）]'
    t0.rows[5].cells[2].text = '[待填写]'
    t0.rows[5].cells[3].text = '[待填写]'
    
    # 评定成绩、评定人与评定日期属于教师评分栏，清空模板示例值（如 100、宋 杰、2025-11-22），严禁当作真实成绩
    t0.rows[6].cells[1].text = ''
    t0.rows[6].cells[3].text = ''
    t0.rows[7].cells[1].text = ''
    t0.rows[7].cells[3].text = ''

    for row in t0.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for r in p.runs:
                    set_run_font(r, east_asia='SimSun', size_pt=10.5)

    print("封面与团队信息表更新完成（评定日期规范设为待填写）")

def update_toc(doc):
    r"""
    配置 Word 原生动态目录字段（TOC \o "1-3" \h \z \u）。
    不再写入硬编码固定页码文本，而是嵌入真实的 Word 原生目录域代码，
    后续通过 Word COM 自动化刷新或 Word 打开时自动更新，确保目录页码与正文排版绝对一致。
    """
    body_elements = list(doc.element.body)
    sdt = None
    for el in body_elements:
        if el.tag.endswith('sdt'):
            sdt = el
            break
    
    if sdt is None:
        print("未找到目录 SDT，跳过目录文本替换")
        return

    sdtContent = sdt.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sdtContent')
    if sdtContent is None:
        return

    for p in list(sdtContent):
        sdtContent.remove(p)

    # 1. 目录标题段落
    p_toc_head = parse_xml(
        f'<w:p {nsdecls("w")}>\n'
        f'  <w:pPr>\n'
        f'    <w:pStyle w:val="TOCHeading"/>\n'
        f'    <w:jc w:val="center"/>\n'
        f'    <w:spacing w:before="120" w:after="120"/>\n'
        f'  </w:pPr>\n'
        f'  <w:r>\n'
        f'    <w:rPr>\n'
        f'      <w:rFonts w:ascii="Times New Roman" w:eastAsia="SimHei"/>\n'
        f'      <w:b/>\n'
        f'      <w:sz w:val="28"/>\n'
        f'    </w:rPr>\n'
        f'    <w:t>目  录</w:t>\n'
        f'  </w:r>\n'
        f'</w:p>'
    )
    sdtContent.append(p_toc_head)

    # 2. 嵌入 Word 原生目录域 (TOC \o "1-3" \h \z \u)
    p_toc_field = parse_xml(
        f'<w:p {nsdecls("w")}>\n'
        f'  <w:pPr>\n'
        f'    <w:pStyle w:val="TOC1"/>\n'
        f'  </w:pPr>\n'
        f'  <w:r><w:fldChar w:fldCharType="begin"/></w:r>\n'
        f'  <w:r><w:instrText xml:space="preserve"> TOC \\o "1-3" \\h \\z \\u </w:instrText></w:r>\n'
        f'  <w:r><w:fldChar w:fldCharType="separate"/></w:r>\n'
        f'  <w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:eastAsia="SimSun"/><w:sz w:val="21"/></w:rPr><w:t>正在更新目录条目与实际页码...</w:t></w:r>\n'
        f'  <w:r><w:fldChar w:fldCharType="end"/></w:r>\n'
        f'</w:p>'
    )
    sdtContent.append(p_toc_field)

    # 3. 启用全局 updateFields 属性
    settings = doc.settings.element
    if settings.find(qn('w:updateFields')) is None:
        settings.append(parse_xml(f'<w:updateFields {nsdecls("w")} w:val="true"/>'))

    print("已嵌入 Word 原生动态目录字段代码，配置了打开/导出自动刷新")
