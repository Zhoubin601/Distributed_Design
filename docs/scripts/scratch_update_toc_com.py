# -*- coding: utf-8 -*-
"""
使用 Word COM 自动化刷新目录字段并导出 PDF 进行排版与页码核对
"""
import os
import sys

def update_fields_and_export_pdf(docx_path, pdf_path):
    abs_docx = os.path.abspath(docx_path)
    abs_pdf = os.path.abspath(pdf_path)
    print(f"正在通过 Word COM 打开文档: {abs_docx}")
    
    import win32com.client
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    
    try:
        doc = word.Documents.Open(abs_docx)
        print("正在更新目录与所有字段...")
        print(f"检测到 Word 目录数量: {doc.TablesOfContents.Count}")
        if doc.TablesOfContents.Count > 0:
            for i in range(1, doc.TablesOfContents.Count + 1):
                doc.TablesOfContents(i).Update()
                print(f"已更新第 {i} 个目录")
        else:
            print("正在通过全局域更新目录...")
            doc.Fields.Update()
        
        doc.Fields.Update()
        
        # 保存更新后的 docx
        doc.Save()
        print(f"已保存更新字段后的 Word 文档: {abs_docx}")
        
        # 导出为 PDF (wdFormatPDF = 17)
        print(f"正在导出 PDF: {abs_pdf}")
        doc.SaveAs(abs_pdf, FileFormat=17)
        print("PDF 导出成功！")
        
        # 统计页数
        page_count = doc.ComputeStatistics(2) # 2 = wdStatisticPages
        print(f"文档总页数 (Word 统计): {page_count} 页")
        
    except Exception as e:
        print(f"COM 自动化执行出错: {e}")
        raise e
    finally:
        doc.Close(SaveChanges=True)
        word.Quit()

if __name__ == "__main__":
    docx_file = sys.argv[1] if len(sys.argv) > 1 else "output/Distributed_Design_Report_Draft_v2.docx"
    pdf_file = sys.argv[2] if len(sys.argv) > 2 else "output/Distributed_Design_Report_Draft_v2.pdf"
    update_fields_and_export_pdf(docx_file, pdf_file)
