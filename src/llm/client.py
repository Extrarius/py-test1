"""OpenRouter LLM клиент — OpenAI-совместимый API."""
import logging
from threading import Semaphore
from typing import Any

from src.config import (
    LLM_CONCURRENCY,
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
)
from src.llm.retry import with_retry

logger = logging.getLogger(__name__)

BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_TIMEOUT = 60.0

_semaphore: Semaphore | None = None


def _get_semaphore() -> Semaphore:
    global _semaphore
    if _semaphore is None:
        _semaphore = Semaphore(LLM_CONCURRENCY)
    return _semaphore


@with_retry(max_retries=3, initial_delay=1.0, backoff_factor=2.0)
def chat(
    messages: list[dict[str, str]],
    model: str | None = None,
    api_key: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> str:
    """
    Отправить запрос в OpenRouter (chat completions).
    Вернуть text ответа.
    Retry при 429/500, лимит параллелизма через Semaphore.
    """
    key = api_key or OPENROUTER_API_KEY
    if not key:
        raise ValueError("OPENROUTER_API_KEY не задан")

    mdl = model or OPENROUTER_MODEL or "google/gemini-flash-1.5"

    sem = _get_semaphore()
    sem.acquire()
    try:
        from openai import OpenAI

        client = OpenAI(
            base_url=BASE_URL,
            api_key=key,
            timeout=timeout,
        )
        resp = client.chat.completions.create(
            model=mdl,
            messages=messages,
        )
        choice = resp.choices[0] if resp.choices else None
        if not choice or not choice.message:
            return ""
        return choice.message.content or ""
    except Exception:
        raise
    finally:
        sem.release()


def summarize_chunk(text: str, system_prompt: str | None = None) -> str:
    """Краткий саммари чанка через LLM."""
    system = system_prompt or (
        "Извлеки ключевые тезисы, факты, цифры и даты. Отвечай кратко на русском."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": text[:15000]},  # лимит контекста
    ]
    return chat(messages)


def chat_cached(
    messages: list[dict[str, str]],
    model: str | None = None,
) -> str:
    """Chat с кешем по hash(prompt + text + model)."""
    from src.config import OPENROUTER_MODEL
    from src.storage.cache import get_llm_cache, set_llm_cache

    mdl = model or OPENROUTER_MODEL or "google/gemini-flash-1.5"
    key = str(messages)
    text = messages[-1].get("content", "") if messages else ""
    cached = get_llm_cache(key, text, mdl)
    if cached is not None:
        return cached
    out = chat(messages, model=mdl)
    set_llm_cache(key, text, mdl, out)
    return out
