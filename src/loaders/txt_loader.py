"""TXT/MD loader — чтение как текст."""
from pathlib import Path

from src.loaders.base import BaseLoader, normalize_text


class TXTLoader(BaseLoader):
    extensions = (".txt", ".md", ".markdown")
    mime_types = ("text/plain", "text/markdown", "text/x-markdown")

    def load(self, path: Path) -> str:
        try:
            for enc in ("utf-8", "utf-8-sig", "cp1251", "latin-1"):
                try:
                    return normalize_text(path.read_text(encoding=enc))
                except UnicodeDecodeError:
                    continue
            return ""
        except Exception:
            return ""
