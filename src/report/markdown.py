"""Генерация Markdown отчёта."""
from pathlib import Path

from src.report.models import DocSummary, ReportData


def build_report_md(
    report: ReportData,
    title: str = "Саммари папки",
    folder_name: str = "",
) -> str:
    """
    Собрать отчёт в Markdown.
    Executive Summary, Карта тем, Ключевые факты, Оглавление, Метаданные.
    """
    lines = []
    lines.append(f"# {title}")
    if folder_name:
        lines.append(f"\n**Папка:** {folder_name}\n")

    lines.append("## Executive Summary\n")
    lines.append(report.executive_summary)
    lines.append("")

    if report.topic_map:
        lines.append("## Карта тем\n")
        for topic in report.topic_map:
            lines.append(f"- {topic}")
        lines.append("")

    if report.key_facts:
        lines.append("## Ключевые факты\n")
        for fact in report.key_facts:
            lines.append(f"- {fact}")
        lines.append("")

    if report.table_of_contents:
        lines.append("## Оглавление\n")
        for doc in report.table_of_contents:
            lines.append(f"### {doc.name}")
            lines.append(f"- **Путь:** `{doc.path}`")
            if doc.mime_type:
                lines.append(f"- **Тип:** {doc.mime_type}")
            if doc.size is not None:
                lines.append(f"- **Размер:** {_fmt_size(doc.size)}")
            lines.append("")
            lines.append(doc.summary)
            lines.append("")

    if report.metadata:
        lines.append("## Метаданные\n")
        lines.append(f"- **Файлов:** {report.metadata.get('file_count', 0)}")
        lines.append(f"- **Общий размер:** {_fmt_size(report.metadata.get('total_size', 0))}")
        types_str = ", ".join(f"{k}: {v}" for k, v in report.metadata.get("types", {}).items())
        if types_str:
            lines.append(f"- **Типы:** {types_str}")
        lines.append("")

    return "\n".join(lines)


def _fmt_size(size: int) -> str:
    """Форматировать размер в байтах."""
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


def build_report_json(report: ReportData) -> str:
    """Собрать отчёт в JSON."""
    import json

    data = {
        "executive_summary": report.executive_summary,
        "topic_map": report.topic_map,
        "key_facts": report.key_facts,
        "table_of_contents": [
            {
                "path": d.path,
                "name": d.name,
                "summary": d.summary,
                "mime_type": d.mime_type,
                "size": d.size,
            }
            for d in report.table_of_contents
        ],
        "metadata": report.metadata,
    }
    return json.dumps(data, ensure_ascii=False, indent=2)
