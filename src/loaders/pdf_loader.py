"""PDF loader — извлечение текста через pypdf."""
from pathlib import Path

from src.loaders.base import BaseLoader, normalize_text


class PDFLoader(BaseLoader):
    extensions = (".pdf",)
    mime_types = ("application/pdf",)

    def load(self, path: Path) -> str:
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            parts = []
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    parts.append(t)
            return normalize_text("\n".join(parts))
        except Exception:
            return ""
