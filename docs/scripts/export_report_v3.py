"""Update and save native Word fields, then export the same layout to PDF."""
from pathlib import Path
import sys
import win32com.client


def export(source):
    source = Path(source).resolve()
    target = source.with_suffix('.pdf')
    word = None
    doc = None
    try:
        word = win32com.client.DispatchEx('Word.Application')
        word.Visible = False
        word.DisplayAlerts = 0
        doc = word.Documents.Open(str(source), AddToRecentFiles=False, Visible=False)
        for _ in range(2):
            doc.Repaginate()
            doc.Fields.Update()
            for i in range(1, doc.TablesOfContents.Count+1):
                doc.TablesOfContents(i).Update()
        doc.Repaginate()
        for i in range(1, doc.TablesOfContents.Count+1):
            doc.TablesOfContents(i).UpdatePageNumbers()
        doc.Save()
        pages = doc.ComputeStatistics(2)
        doc.ExportAsFixedFormat(str(target), 17, False, 0, 0, 1, 1, 0,
                                True, True, 1, True, True, False)
        print(f'Saved Word fields and PDF: {pages} pages')
    finally:
        if doc is not None:
            doc.Close(SaveChanges=0)
        if word is not None:
            word.Quit(SaveChanges=0)


if __name__ == '__main__':
    export(sys.argv[1])
