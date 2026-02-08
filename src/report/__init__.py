"""Генерация отчёта: Markdown, JSON."""

from src.report.builder import build_report
from src.report.markdown import build_report_md, build_report_json
from src.report.models import DocSummary, ReportData

__all__ = ["DocSummary", "ReportData", "build_report", "build_report_md", "build_report_json"]
