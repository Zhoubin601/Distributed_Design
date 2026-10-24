"""Resolve versioned report paths without relocating the user's files."""
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[2]


def resolve_report_docx():
    override = os.environ.get('REPORT_DOCX')
    if override:
        return str(Path(override).resolve())
    for folder, pattern in [('output/v4', '*-v4.docx'),
                            ('output/v3', '*-v3.docx'),
                            ('output/v2', '*v2.docx'),
                            ('output', '*v2.docx'),
                            ('output/v1', '*v1.docx'),
                            ('output', '*v1.docx')]:
        candidates = sorted((ROOT/folder).glob(pattern))
        if candidates:
            return str(candidates[-1])
    return str(ROOT/'output/v3/20261024-misttable-distributed-design-v3.docx')


def resolve_report_pdf():
    return str(Path(resolve_report_docx()).with_suffix('.pdf'))
