"""Разбиение текста на чанки по абзацам, лимит токенов, overlap."""
from typing import Iterator

from src.chunking.models import Chunk
from src.chunking.tokenizer import estimate_tokens, split_into_sentences


def chunk_text(
    text: str,
    file_id: str,
    path: str = "",
    max_tokens: int = 4000,
    overlap_tokens: int | None = None,
    overlap_ratio: float = 0.08,
) -> list[Chunk]:
    """
    Разбить текст на чанки.
    - Разбиение по абзацам (приоритет границ)
    - Лимит max_tokens на чанк
    - Overlap overlap_ratio (5–10%) или overlap_tokens для связности
    - Метаданные: file_id, chunk_index, start_char, end_char, token_estimate
    """
    if overlap_tokens is None:
        overlap_tokens = int(max_tokens * overlap_ratio)
    overlap_tokens = max(0, min(overlap_tokens, max_tokens // 2))

    paragraphs = split_into_sentences(text)
    if not paragraphs:
        return []

    chunks: list[Chunk] = []
    current: list[str] = []
    current_tokens = 0
    chunk_start = 0

    def flush(overlap_paras: list[str] | None = None) -> int:
        nonlocal current, current_tokens, chunk_start
        if not current:
            return chunk_start
        chunk_text_str = "\n\n".join(current)
        chunk_len = sum(len(p) + 2 for p in current) - 2
        chunk_end = chunk_start + chunk_len
        token_est = estimate_tokens(chunk_text_str)
        chunks.append(
            Chunk(
                text=chunk_text_str,
                file_id=file_id,
                chunk_index=len(chunks),
                start_char=chunk_start,
                end_char=chunk_end,
                token_estimate=token_est,
                path=path,
            )
        )
        current = list(overlap_paras) if overlap_paras else []
        current_tokens = estimate_tokens("\n\n".join(current)) if current else 0
        if overlap_paras:
            overlap_len = sum(len(p) + 2 for p in overlap_paras) - 2
            chunk_start = chunk_end - overlap_len
        else:
            chunk_start = chunk_end + 2
        return chunk_start

    for para in paragraphs:
        para_tokens = estimate_tokens(para)
        if current_tokens + para_tokens > max_tokens and current:
            overlap_paras = []
            if overlap_tokens > 0:
                acc = 0
                for p in reversed(current):
                    pt = estimate_tokens(p) + 2
                    if acc + pt <= overlap_tokens:
                        overlap_paras.insert(0, p)
                        acc += pt
                    else:
                        break
            flush(overlap_paras)

        current.append(para)
        current_tokens += para_tokens + 2

    flush()
    return chunks


def chunk_text_simple(
    text: str,
    file_id: str,
    path: str = "",
    max_tokens: int = 4000,
    overlap_ratio: float = 0.08,
) -> Iterator[Chunk]:
    """Итератор по чанкам."""
    for c in chunk_text(text, file_id, path, max_tokens, overlap_ratio=overlap_ratio):
        yield c
