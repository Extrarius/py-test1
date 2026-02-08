"""Chunks → Doc: свести чанки в саммари документа."""
from src.chunking import Chunk
from src.llm.client import chat_cached
from src.llm.prompts import load_prompt


def chunks_to_doc_summary(chunks: list[Chunk]) -> str:
    """Свести чанки в краткое саммари документа (5–10 тезисов)."""
    if not chunks:
        return ""
    if len(chunks) == 1:
        return _summarize_chunk(chunks[0].text)
    summaries = [_summarize_chunk(c.text) for c in chunks]
    prompt = load_prompt("doc") or "Объедини саммари в единый документ. 5–10 тезисов. На русском."
    merged = "\n---\n".join(summaries)
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": merged[:12000]},
    ]
    return chat_cached(messages)


def _summarize_chunk(text: str) -> str:
    """Саммари одного чанка (с кешем)."""
    prompt = load_prompt("chunk") or "Извлеки тезисы и факты. Кратко на русском."
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": text[:15000]},
    ]
    return chat_cached(messages)
