"""Фабрика источников — Drive API / local / public link."""
from pathlib import Path
from typing import Literal

from src.config import GOOGLE_CREDENTIALS_PATH, PROJECT_ROOT
from src.sources.base import BaseSource
from src.sources.drive_source import DriveSource
from src.sources.local_source import LocalSource

_SOURCES: dict[str, type[BaseSource]] = {
    "drive": DriveSource,
    "local": LocalSource,
}


def get_source(
    name: Literal["drive", "local"] = "drive",
    credentials_path: Path | str | None = None,
) -> BaseSource:
    """Вернуть источник по имени. drive — Drive API, local — локальная папка."""
    cls = _SOURCES.get(name, DriveSource)
    if name == "drive":
        return cls(credentials_path=credentials_path or PROJECT_ROOT / GOOGLE_CREDENTIALS_PATH)
    return cls()


def register_source(name: str, source_cls: type[BaseSource]) -> None:
    """Добавить новый источник."""
    _SOURCES[name] = source_cls
