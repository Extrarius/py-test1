"""Фабрика loaders — регистр по расширению, легко добавить новый формат."""
from pathlib import Path
from typing import Type

from src.loaders.base import BaseLoader
from src.loaders.pdf_loader import PDFLoader
from src.loaders.docx_loader import DOCXLoader
from src.loaders.txt_loader import TXTLoader

_REGISTRY: dict[str, BaseLoader] = {}
_INITIALIZED = False


def _init_registry() -> None:
    global _INITIALIZED
    if _INITIALIZED:
        return
    for loader_cls in (PDFLoader, DOCXLoader, TXTLoader):
        loader = loader_cls()
        for ext in loader.extensions:
            _REGISTRY[ext.lower()] = loader
    _INITIALIZED = True


def get_loader(path: Path | str) -> BaseLoader | None:
    """Вернуть loader по расширению файла или None."""
    _init_registry()
    ext = Path(path).suffix.lower()
    return _REGISTRY.get(ext)


def load_text(path: Path | str) -> str:
    """Извлечь и нормализовать текст из файла."""
    p = Path(path)
    loader = get_loader(p)
    if loader:
        return loader.load_normalized(p)
    return ""


def register_loader(extensions: tuple[str, ...], loader_cls: Type[BaseLoader]) -> None:
    """Добавить новый loader. Пример: register_loader(('.pptx',), PPTXLoader)"""
    loader = loader_cls()
    for ext in extensions:
        _REGISTRY[ext.lower()] = loader
