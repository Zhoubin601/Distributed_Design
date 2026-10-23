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
    
    # 评定日期由教师评定时填写，不硬编码虚假日期
    t0.rows[7].cells[3].text = '[待教师填写]'

    for row in t0.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for r in p.runs:
                    set_run_font(r, east_asia='SimSun', size_pt=10.5)

    print("封面与团队信息表更新完成（评定日期规范设为待填写）")

def update_toc(doc):
    """更新目录块中的条目骨架，设置自动更新标记"""
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
        if p.tag.endswith('p'):
            sdtContent.remove(p)

    toc_items = [
        ("1. 系统简介", 1, "4"),
        ("  1.1 系统背景与业务定位", 2, "4"),
        ("  1.2 为什么属于分布式系统", 2, "4"),
        ("  1.3 核心业务功能与角色权限", 2, "5"),
        ("  1.4 分布式技术需求与设计假设", 2, "5"),
        ("  1.5 课件理论联系：分布式系统的目标、挑战与事务边界", 2, "6"),
        ("2. 体系结构", 1, "7"),
        ("  2.1 技术需求", 2, "7"),
        ("  2.2 概要设计", 2, "7"),
        ("    (1) 客户端—服务器分层协作架构", 3, "7"),
        ("    (2) 房间级单权威处理路径与扩展方式", 3, "8"),
        ("    (3) 核心架构选型对比", 3, "9"),
        ("3. 进程", 1, "10"),
        ("  3.1 技术需求", 2, "10"),
        ("  3.2 概要设计", 2, "10"),
        ("    (1) 客户端与服务端进程职责分工", 3, "10"),
        ("    (2) 多房间分配与并行处理方式", 3, "11"),
        ("    (3) 课件理论分析：并发模型、虚拟化与代码迁移适用性", 3, "12"),
        ("4. 通信", 1, "13"),
        ("  4.1 技术需求", 2, "13"),
        ("  4.2 概要设计", 2, "13"),
        ("    (1) 请求—应答与实时协作的通信分工", 3, "13"),
        ("    (2) 角色标记移动与状态传播时序", 3, "14"),
        ("    (3) 课件理论分析：瞬态通信 vs 持久通信、消息广播与恢复边界", 3, "15"),
        ("5. 命名", 1, "16"),
        ("  5.1 技术需求", 2, "16"),
        ("  5.2 概要设计", 2, "16"),
        ("    (1) 稳定实体标识设计", 3, "16"),
        ("    (2) 邀请码凭证与房间定位机制", 3, "17"),
        ("    (3) 课件理论分析：平面命名、结构化命名与 DHT/Chord 方案对比", 3, "17"),
        ("6. 同步", 1, "18"),
        ("  6.1 技术需求", 2, "18"),
        ("  6.2 概要设计", 2, "18"),
        ("    (1) 基于房间权威定序与对象版本的冲突处理机制", 3, "18"),
        ("    (2) 掷骰与状态判定的有序性保障", 3, "19"),
        ("    (3) 课件理论分析：物理时钟偏差、逻辑时钟与并发控制算法比较", 3, "20"),
        ("7. 一致性与复制", 1, "21"),
        ("  7.1 技术需求", 2, "21"),
        ("  7.2 概要设计", 2, "21"),
        ("    (1) 业务分级一致性模型构建", 3, "21"),
        ("    (2) 战争迷雾与成员权限的状态投影隔离", 3, "22"),
        ("    (3) 课件理论分析：主备复制与 Quorum 仲裁机制对比", 3, "23"),
        ("8. 容错性与故障恢复", 1, "24"),
        ("  8.1 技术需求", 2, "24"),
        ("  8.2 概要设计", 2, "24"),
        ("    (1) 网络超时分析与基于 operationId 的幂等重试机制", 3, "24"),
        ("    (2) 客户端断线重连与增量/全量快照差分恢复流程", 3, "25"),
        ("    (3) 协作服务异常接管与写隔离前提", 3, "26"),
        ("    (4) 课件理论分析：故障分类模型、可靠通信与分布式提交适用边界", 3, "26"),
        ("9. 总结", 1, "27"),
        ("  9.1 系统设计与分布式知识点对应回顾", 2, "27"),
        ("  9.2 核心设计取舍与工程理性总结", 2, "28"),
        ("  9.3 设计局限性与未验证假设声明", 2, "28"),
        ("参考文献", 1, "29"),
        ("附录 (得分栏勿填)", 1, "30")
    ]

    p_toc_head = parse_xml(f'<w:p {nsdecls("w")}><w:pPr><w:pStyle w:val="TOCHeading"/><w:jc w:val="center"/><w:spacing w:before="120" w:after="120"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:eastAsia="SimHei"/><w:b/><w:sz w:val="28"/></w:rPr><w:t>目  录</w:t></w:r></w:p>')
    sdtContent.append(p_toc_head)

    for title, level, page_str in toc_items:
        style_name = f"toc{level}" if level > 1 else "toc1"
        p_xml = parse_xml(
            f'<w:p {nsdecls("w")}>\n'
            f'  <w:pPr>\n'
            f'    <w:pStyle w:val="{style_name}"/>\n'
            f'    <w:tabs><w:tab w:val="right" w:leader="dot" w:pos="9350"/></w:tabs>\n'
            f'    <w:spacing w:before="24" w:after="24"/>\n'
            f'  </w:pPr>\n'
            f'  <w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:eastAsia="SimSun"/><w:sz w:val="21"/></w:rPr><w:t>{title}</w:t></w:r>\n'
            f'  <w:r><w:tab/></w:r>\n'
            f'  <w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:eastAsia="SimSun"/><w:sz w:val="21"/></w:rPr><w:t>{page_str}</w:t></w:r>\n'
            f'</w:p>'
        )
        sdtContent.append(p_xml)

    # 启用全局 updateFields 属性
    settings = doc.settings.element
    if settings.find(qn('w:updateFields')) is None:
        settings.append(parse_xml(f'<w:updateFields {nsdecls("w")} w:val="true"/>'))

    print("目录条目结构更新完成，已配置 Word 打开时自动更新目录字段")
