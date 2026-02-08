"""Кеш: файлы, тексты, результаты LLM."""

from src.storage.cache import get_llm_cache, set_llm_cache
from src.storage.load_cached import load_cached_files

__all__ = ["get_llm_cache", "set_llm_cache", "load_cached_files"]
