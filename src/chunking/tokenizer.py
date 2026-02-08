"""Оценка токенов: tiktoken или ~4 символа = 1 токен."""
from typing import List


def estimate_tokens(text: str, model: str = "gpt-4") -> int:
    """Оценка токенов. При ошибке tiktoken — fallback ~4 символа = 1 токен."""
    try:
        import tiktoken
        enc = tiktoken.encoding_for_model(model)
        return len(enc.encode(text))
    except Exception:
        return _chars_to_tokens(text)


def _chars_to_tokens(text: str) -> int:
    """Приблизительно: ~4 символа = 1 токен."""
    return (len(text) + 3) // 4


def split_into_sentences(text: str) -> List[str]:
    """Разбить на абзацы (по двойному переносу) и строки."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return paragraphs
