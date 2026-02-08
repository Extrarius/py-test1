"""Сборка ReportData из глобального саммари и метаданных."""
import re
from collections import Counter
from typing import Any

from src.report.models import DocSummary, ReportData
from src.sources.models import FileMeta


def build_report(
    global_summary: str,
    doc_summaries: list[tuple[str, str, str]] | None = None,
    files_meta: list[FileMeta] | None = None,
) -> ReportData:
    """
    Собрать ReportData.
    doc_summaries: [(path, name, summary), ...]
    files_meta: список FileMeta для метаданных и оглавления.
    """
    doc_summaries = doc_summaries or []
    files_meta = files_meta or []

    exec_summary, topic_map, key_facts = _parse_summary(global_summary)

    toc: list[DocSummary] = []
    path_to_meta = {(f.path if hasattr(f, "path") else f.get("path", "")): f for f in files_meta}
    for path, name, summary in doc_summaries:
        meta = path_to_meta.get(path, None)
        mime = meta.mime_type if meta and hasattr(meta, "mime_type") else (meta.get("mime_type", "") if meta else "")
        size = meta.size if meta and hasattr(meta, "size") else (meta.get("size") if meta else None)
        toc.append(
            DocSummary(
                path=path,
                name=name,
                summary=summary,
                mime_type=mime,
                size=size,
            )
        )

    def _size(f): return f.size if hasattr(f, "size") else f.get("size")
    def _mime(f): return f.mime_type if hasattr(f, "mime_type") else f.get("mime_type")
    total_size = sum(_size(f) or 0 for f in files_meta)
    type_counts = Counter(_mime(f) or "unknown" for f in files_meta)
    metadata: dict[str, Any] = {
        "file_count": len(files_meta),
        "total_size": total_size,
        "types": dict(type_counts),
    }

    return ReportData(
        executive_summary=exec_summary,
        topic_map=topic_map,
        key_facts=key_facts,
        table_of_contents=toc,
        metadata=metadata,
        raw_summary=global_summary,
    )


def _parse_summary(text: str) -> tuple[str, list[str], list[str]]:
    """
    Разобрать саммари на секции (упрощённо).
    Если LLM вернул структурированный текст — извлечь Executive Summary, темы, факты.
    Иначе — exec_summary = весь текст, темы/факты пусты.
    """
    exec_summary = text.strip()
    topic_map: list[str] = []
    key_facts: list[str] = []

    lower = text.lower()
    if "executive summary" in lower or "резюме" in lower:
        parts = re.split(r"\n##?\s*(?:Executive Summary|Резюме|карта тем|ключевые факты)\s*\n", text, flags=re.I)
        if parts:
            exec_summary = parts[0].strip()
        if len(parts) > 1:
            for p in parts[1:]:
                for line in p.split("\n"):
                    line = line.strip()
                    if line.startswith("-") or line.startswith("*"):
                        line = line.lstrip("-* ").strip()
                        if any(c.isdigit() for c in line) or "http" in line or "/" in line:
                            key_facts.append(line)
                        else:
                            topic_map.append(line)

    if not topic_map and not key_facts:
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("-") or line.startswith("*"):
                line = line.lstrip("-* ").strip()
                if line and (any(c.isdigit() for c in line) or "http" in line):
                    key_facts.append(line)
                elif line and len(line) > 3:
                    topic_map.append(line)

    return (exec_summary, topic_map[:15], key_facts[:20])
