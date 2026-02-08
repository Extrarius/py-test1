"""Кеш LLM по hash(prompt + text + model)."""
import hashlib
import json
from pathlib import Path

from src.config import CACHE_LLM, ensure_cache_dirs


def _hash_key(prompt: str, text: str, model: str) -> str:
    return hashlib.sha256(f"{prompt}|{text}|{model}".encode()).hexdigest()


def get_llm_cache(prompt: str, text: str, model: str) -> str | None:
    """Вернуть кешированный ответ или None."""
    ensure_cache_dirs()
    key = _hash_key(prompt, text, model)
    path = CACHE_LLM / f"{key}.json"
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data.get("content")
        except (json.JSONDecodeError, OSError):
            pass
    return None


def set_llm_cache(prompt: str, text: str, model: str, content: str) -> None:
    """Сохранить ответ в кеш."""
    ensure_cache_dirs()
    key = _hash_key(prompt, text, model)
    path = CACHE_LLM / f"{key}.json"
    path.write_text(
        json.dumps({"content": content, "model": model}, ensure_ascii=False, indent=0),
        encoding="utf-8",
    )
