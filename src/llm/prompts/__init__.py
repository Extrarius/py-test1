"""Промпты для саммаризации."""
from pathlib import Path

_PROMPTS_DIR = Path(__file__).resolve().parent


def load_prompt(name: str) -> str:
    """Загрузить промпт из файла."""
    path = _PROMPTS_DIR / f"{name}.txt"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return ""
