"""Regression cases for the two false passes and fixed-page assumptions."""
import sys
from pathlib import Path

import docx
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'docs/scripts'))
from scratch_verify_output import has_real_value, find_body_page, ReportVerifier
from report_paths import resolve_report_docx, resolve_report_pdf


@pytest.mark.parametrize('value', ['', '  ', '[待填写]', '待确认', 'TODO'])
def test_placeholder_is_not_filled_team_info(value):
    assert not has_real_value(value)


def test_real_group_is_filled():
    assert has_real_value('课程设计小组')


class Page:
    def __init__(self, text):
        self.text = text

    def get_text(self):
        return self.text


def test_body_heading_on_fourth_page_ignores_toc():
    pdf = [Page('封面'), Page('1. 系统简介......4\n1.1 系统背景与业务定位......4'),
           Page('目录续'), Page('1. 系统简介\n1.1 系统背景与业务定位\n正文')]
    assert find_body_page(pdf, '1. 系统简介', '1.1 系统背景与业务定位') == 4


def test_absent_heading_is_not_silently_accepted():
    assert find_body_page([Page('参考文献......25')], '参考文献') == -1


def test_actual_document_placeholder_regression_rejected():
    d = docx.Document(resolve_report_docx())
    d.tables[-1].rows[2].cells[0].text = '[待填写]'
    v = ReportVerifier(resolve_report_docx(), resolve_report_pdf())
    v.verify_appendix(d)
    assert any(status == 'FAIL' and '组名' in name for _, name, status, _ in v.results)
