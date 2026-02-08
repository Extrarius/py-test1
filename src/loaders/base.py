"""Базовый интерфейс loader — извлечение текста из файла."""
from pathlib import Path
from abc import ABC, abstractmethod


def normalize_text(text: str) -> str:
    """Нормализация: убрать лишние пробелы, унифицировать переносы."""
    if not text or not isinstance(text, str):
        return ""
    import re
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)  # множественные пробелы → один
    text = re.sub(r"\n{3,}", "\n\n", text)  # 3+ переносов → 2
    return text.strip()


class BaseLoader(ABC):
    """Базовый класс loader — наследники реализуют load()."""

    extensions: tuple[str, ...] = ()
    mime_types: tuple[str, ...] = ()

    @abstractmethod
    def load(self, path: Path) -> str:
        """Извлечь текст из файла. Вернуть пустую строку при ошибке."""
        pass

    def load_normalized(self, path: Path) -> str:
        """Извлечь и нормализовать текст."""
        return normalize_text(self.load(path))
