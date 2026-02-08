"""Folder → Global: финальный общий саммари папки."""
from src.llm.client import chat_cached
from src.llm.prompts import load_prompt


def folder_to_global_summary(folder_summaries: list[str]) -> str:
    """Финальный общий саммари: Executive Summary, карта тем, ключевые факты."""
    if not folder_summaries:
        return ""
    if len(folder_summaries) == 1:
        return folder_summaries[0]
    prompt = load_prompt("global") or (
        "Создай финальное саммари: Executive Summary (1–2 абзаца), карта тем, ключевые факты. На русском."
    )
    merged = "\n---\n".join(folder_summaries)
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": merged[:15000]},
    ]
    return chat_cached(messages)
