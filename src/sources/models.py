"""Модели для источника файлов."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class FileMeta:
    """Метаданные файла из Google Drive."""

    file_id: str
    name: str
    mime_type: str
    size: int | None
    modified_time: str | None
    path: str  # путь внутри папки, напр. "docs/report.pdf"
    is_folder: bool
    local_path: Path | None = None  # путь в кеше после скачивания
