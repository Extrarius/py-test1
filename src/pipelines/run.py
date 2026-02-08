"""Полный пайплайн: ingest → summarize → report."""
import json
import logging
from pathlib import Path

from tqdm import tqdm

from src.chunking import chunk_text
from src.config import CACHE_DIR, CHUNK_TOKENS, ensure_cache_dirs
from src.loaders import load_text
from src.pipelines import chunks_to_doc_summary, docs_to_folder_summary, folder_to_global_summary
from src.report import build_report, build_report_md, build_report_json
from src.sources.models import FileMeta
from src.storage.load_cached import load_cached_files

logger = logging.getLogger(__name__)
SUMMARY_RESULT_PATH = CACHE_DIR / "summary_result.json"
ERRORS_LOG_PATH = CACHE_DIR / "errors.log"


def _log_error(path: str, reason: str) -> None:
    """Логировать ошибку и в logger, и в файл .cache/errors.log."""
    msg = f"Ошибка: {path} — {reason}"
    logger.warning(msg)
    ensure_cache_dirs()
    try:
        with open(ERRORS_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except OSError:
        pass


def run_summarize(
    files_meta: list[FileMeta],
    max_files: int | None = None,
    progress: bool = True,
) -> dict:
    """
    Прогнать саммаризацию по файлам.
    Graceful degradation: ошибка на одном файле → логировать и идти дальше.
    Вернуть dict: {global_summary, doc_summaries, files_meta, failed: [{path, reason}]}
    """
    ensure_cache_dirs()
    if max_files:
        files_meta = files_meta[:max_files]

    doc_summaries: list[tuple[str, str, str]] = []
    failed: list[dict] = []
    it = tqdm(files_meta, desc="Саммаризация", unit="файл") if progress else files_meta

    for meta in it:
        try:
            if not meta.local_path or not meta.local_path.exists():
                _log_error(meta.path, "файл не найден")
                failed.append({"path": meta.path, "reason": "файл не найден"})
                continue
            text = load_text(meta.local_path)
            if not text.strip():
                _log_error(meta.path, "пустой текст")
                failed.append({"path": meta.path, "reason": "пустой текст"})
                continue
            chunks = chunk_text(
                text,
                file_id=meta.file_id,
                path=meta.path,
                max_tokens=CHUNK_TOKENS,
            )
            if not chunks:
                _log_error(meta.path, "нет чанков")
                failed.append({"path": meta.path, "reason": "нет чанков"})
                continue
            summary = chunks_to_doc_summary(chunks)
            doc_summaries.append((meta.path, meta.name, summary))
        except Exception as e:
            _log_error(meta.path, str(e))
            failed.append({"path": meta.path, "reason": str(e)})

    if not doc_summaries:
        return {
            "global_summary": "",
            "doc_summaries": [],
            "files_meta": [],
            "failed": failed,
        }

    folder_summary = docs_to_folder_summary(
        [s[2] for s in doc_summaries],
        folder_name="",
    )
    global_summary = folder_to_global_summary([folder_summary])

    return {
        "global_summary": global_summary,
        "doc_summaries": doc_summaries,
        "files_meta": [
            {
                "file_id": f.file_id,
                "name": f.name,
                "mime_type": f.mime_type,
                "size": f.size,
                "path": f.path,
            }
            for f in files_meta
        ],
        "failed": failed,
    }


def save_summary_result(result: dict) -> Path:
    """Сохранить результат саммаризации в кеш."""
    ensure_cache_dirs()
    data = {
        "global_summary": result.get("global_summary", ""),
        "doc_summaries": result.get("doc_summaries", []),
        "files_meta": result.get("files_meta", []),
        "failed": result.get("failed", []),
    }
    SUMMARY_RESULT_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return SUMMARY_RESULT_PATH


def load_summary_result() -> dict | None:
    """Загрузить результат саммаризации из кеша."""
    if not SUMMARY_RESULT_PATH.exists():
        return None
    try:
        return json.loads(SUMMARY_RESULT_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
