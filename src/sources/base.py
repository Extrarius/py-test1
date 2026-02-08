"""Базовый интерфейс источника файлов — Drive API / local / public link."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from src.sources.models import FileMeta


class BaseSource(ABC):
    """Базовый класс источника — наследники реализуют ingest()."""

    @abstractmethod
    def ingest(
        self,
        *,
        folder_id: str | None = None,
        path: Path | str | None = None,
        force: bool = False,
        **kwargs: Any,
    ) -> list[FileMeta]:
        """
        Получить список файлов и скачать в кеш (если нужно).
        folder_id — для Drive API
        path — для локальной папки
        Вернуть list[FileMeta] с заполненным local_path.
        """
        pass
