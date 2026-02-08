"""Парсеры документов: PDF, DOCX, TXT, MD."""

from src.loaders.base import BaseLoader, normalize_text
from src.loaders.factory import get_loader, load_text, register_loader

__all__ = ["BaseLoader", "normalize_text", "get_loader", "load_text", "register_loader"]
