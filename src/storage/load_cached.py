"""Загрузка списка файлов из кеша после ingest."""
import json
from pathlib import Path

from src.config import CACHE_DOWNLOADS, ensure_cache_dirs
from src.sources.models import FileMeta


def load_cached_files(max_files: int | None = None) -> list[FileMeta]:
    """Вернуть список FileMeta из кеша .cache/downloads/."""
    ensure_cache_dirs()
    files: list[FileMeta] = []
    if not CACHE_DOWNLOADS.exists():
        return files
    for dir_path in CACHE_DOWNLOADS.iterdir():
        if not dir_path.is_dir():
            continue
        meta_path = dir_path / "meta.json"
        if not meta_path.exists():
            continue
        try:
            data = json.loads(meta_path.read_text(encoding="utf-8"))
            local_path = data.get("local_path")
            if not local_path or not Path(local_path).exists():
                continue
            meta = FileMeta(
                file_id=data.get("file_id", dir_path.name),
                name=data.get("name", ""),
                mime_type=data.get("mime_type", ""),
                size=data.get("size"),
                modified_time=data.get("modified_time"),
                path=data.get("path", ""),
                is_folder=False,
                local_path=Path(local_path),
            )
            files.append(meta)
            if max_files and len(files) >= max_files:
                break
        except (json.JSONDecodeError, OSError, KeyError):
            continue
    return files
