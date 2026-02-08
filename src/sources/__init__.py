"""Источники файлов: Drive API, local, public link."""

from src.sources.base import BaseSource
from src.sources.drive_api import ingest
from src.sources.factory import get_source, register_source
from src.sources.models import FileMeta

__all__ = ["BaseSource", "FileMeta", "get_source", "ingest", "register_source"]
