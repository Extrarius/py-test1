"""Модели для chunking."""
from dataclasses import dataclass


@dataclass
class Chunk:
    """Чанк текста с метаданными."""

    text: str
    file_id: str
    chunk_index: int
    start_char: int
    end_char: int
    token_estimate: int
    path: str = ""  # путь внутри папки
