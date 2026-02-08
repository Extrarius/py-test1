"""Docs → Folder: обобщить саммари документов в саммари папки."""
from src.llm.client import chat_cached
from src.llm.prompts import load_prompt


def docs_to_folder_summary(doc_summaries: list[str], folder_name: str = "") -> str:
    """Обобщить саммари документов в саммари папки."""
    if not doc_summaries:
        return ""
    if len(doc_summaries) == 1:
        return doc_summaries[0]
    prompt = load_prompt("folder") or "Обобщи саммари документов. Ключевые темы, факты. На русском."
    merged = "\n---\n".join(doc_summaries)
    ctx = f"Папка: {folder_name}\n\n" if folder_name else ""
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": ctx + merged[:12000]},
    ]
    return chat_cached(messages)
