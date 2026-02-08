"""Локальная папка — источник файлов без Drive API."""
from pathlib import Path
from typing import Any

from src.config import CACHE_DOWNLOADS, ensure_cache_dirs
from src.sources.base import BaseSource
from src.sources.models import FileMeta


class LocalSource(BaseSource):
    """Источник: локальная папка на диске."""

    def ingest(
        self,
        *,
        folder_id: str | None = None,
        path: Path | str | None = None,
        force: bool = False,
        **kwargs: Any,
    ) -> list[FileMeta]:
        """Сканировать локальную папку, вернуть FileMeta с local_path."""
        ensure_cache_dirs()
        root = Path(path) if path else Path(".")
        if not root.exists() or not root.is_dir():
            return []

        files: list[FileMeta] = []
        for p in root.rglob("*"):
            if p.is_file():
                rel = p.relative_to(root)
                name = p.name
                ext = p.suffix.lower()
                if ext in (".pdf", ".docx", ".txt", ".md"):
                    meta = FileMeta(
                        file_id=str(p.stat().st_ino) if p.stat().st_ino else str(hash(str(p))),
                        name=name,
                        mime_type="",
                        size=p.stat().st_size,
                        modified_time=str(p.stat().st_mtime),
                        path=str(rel).replace("\\", "/"),
                        is_folder=False,
                        local_path=p.resolve(),
                    )
                    files.append(meta)
        return files
