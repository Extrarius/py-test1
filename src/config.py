"""Загрузка конфигурации из .env и config.yaml."""

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Загружаем .env при импорте
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)
else:
    load_dotenv()  # ищем .env в cwd


def get_env(key: str, default: str | None = None) -> str | None:
    """Получить переменную окружения."""
    return os.environ.get(key, default)


def load_yaml_config() -> dict[str, Any]:
    """Загрузить config.yaml."""
    config_path = Path(__file__).resolve().parent.parent / "config.yaml"
    if not config_path.exists():
        return {}
    try:
        import yaml
        with open(config_path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        return {}


YAML_CONFIG = load_yaml_config()

OPENROUTER_API_KEY: str | None = get_env("OPENROUTER_API_KEY")
GOOGLE_CREDENTIALS_PATH: str = get_env("GOOGLE_CREDENTIALS_PATH") or "credentials.json"
GOOGLE_DRIVE_FOLDER_ID: str = get_env("GOOGLE_DRIVE_FOLDER_ID") or "1x6EKNkVw6PlFVTr6cGrsVscmRuwqGrXd"
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
CACHE_DIR: Path = PROJECT_ROOT / ".cache"
CACHE_DOWNLOADS: Path = CACHE_DIR / "downloads"
CACHE_TEXTS: Path = CACHE_DIR / "texts"
CACHE_LLM: Path = CACHE_DIR / "llm"

MODE: str = str(YAML_CONFIG.get("mode", "fast"))
SOURCE: str = str(YAML_CONFIG.get("source", "drive"))
CHUNK_TOKENS: int = int(YAML_CONFIG.get("chunk_tokens", 4000))
LLM_CONCURRENCY: int = int(YAML_CONFIG.get("llm_concurrency", 2))
OPENROUTER_MODEL: str = get_env("OPENROUTER_MODEL") or str(YAML_CONFIG.get("model", "google/gemini-flash-1.5"))


def ensure_cache_dirs() -> None:
    """Создать директории кеша при необходимости."""
    for d in (CACHE_DIR, CACHE_DOWNLOADS, CACHE_TEXTS, CACHE_LLM):
        d.mkdir(parents=True, exist_ok=True)


def check_api_key() -> bool:
    """Проверить, задан ли OPENROUTER_API_KEY."""
    key = get_env("OPENROUTER_API_KEY")
    return bool(key and key != "sk-or-v1-...")
