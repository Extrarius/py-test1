"""Модели для отчёта."""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DocSummary:
    """Саммари документа для оглавления."""

    path: str
    name: str
    summary: str
    mime_type: str = ""
    size: int | None = None


@dataclass
class ReportData:
    """Структура итогового отчёта."""

    executive_summary: str
    topic_map: list[str] = field(default_factory=list)
    key_facts: list[str] = field(default_factory=list)
    table_of_contents: list[DocSummary] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    raw_summary: str = ""
