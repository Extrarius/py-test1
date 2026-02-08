"""Google Drive API — ингест файлов."""

import json
import logging
from pathlib import Path
from typing import Generator

from tqdm import tqdm

from src.config import CACHE_DOWNLOADS, ensure_cache_dirs
from src.sources.models import FileMeta

logger = logging.getLogger(__name__)

# MIME типы для пропуска
SKIP_MIME = frozenset([
    "application/vnd.google-apps.shortcut",
    "application/vnd.google-apps.form",
])
FOLDER_MIME = "application/vnd.google-apps.folder"

# MIME для экспорта Google Docs/Sheets/Slides
EXPORT_MIME = {
    "application/vnd.google-apps.document": "application/pdf",  # или text/plain
    "application/vnd.google-apps.spreadsheet": "text/csv",
    "application/vnd.google-apps.presentation": "application/pdf",
}


def _get_service(credentials_path: Path):
    """Создать Drive API service с OAuth2 (Desktop OAuth, run_local_server)."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
    creds_path = str(Path(credentials_path).resolve())
    token_path = str(Path(credentials_path).resolve().parent / "token.json")

    # Фиксированный порт 8080 — redirect_uri = http://localhost:8080/
    # ВАЖНО: Добавьте в Google Cloud Console → Credentials → OAuth Client →
    # Authorized redirect URIs: http://localhost:8080/
    REDIRECT_PORT = 8080

    creds = None
    if Path(token_path).exists():
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            flow.redirect_uri = "http://localhost:8080/"  # явно — иначе redirect_uri не попадёт в URL
            creds = flow.run_local_server(port=REDIRECT_PORT)
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    return build("drive", "v3", credentials=creds)


def list_files(
    service,
    folder_id: str,
    path_prefix: str = "",
) -> Generator[FileMeta, None, None]:
    """Рекурсивно получить список файлов в папке."""
    page_token = None
    while True:
        resp = (
            service.files()
            .list(
                q=f"'{folder_id}' in parents and trashed = false",
                pageSize=100,
                pageToken=page_token,
                fields="nextPageToken, files(id, name, mimeType, size, modifiedTime)",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            )
            .execute()
        )
        for f in resp.get("files", []):
            meta = FileMeta(
                file_id=f["id"],
                name=f["name"],
                mime_type=f.get("mimeType", ""),
                size=int(f["size"]) if f.get("size") else None,
                modified_time=f.get("modifiedTime"),
                path=f"{path_prefix}{f['name']}".strip("/"),
                is_folder=f.get("mimeType") == FOLDER_MIME,
            )
            if meta.mime_type in SKIP_MIME:
                continue
            if meta.is_folder:
                yield meta
                yield from list_files(service, meta.file_id, f"{meta.path}/")
            else:
                yield meta
        page_token = resp.get("nextPageToken")
        if not page_token:
            break


def _cache_meta_path(file_id: str) -> Path:
    """Путь к файлу метаданных в кеше."""
    return CACHE_DOWNLOADS / file_id / "meta.json"


def _cached_modified_time(file_id: str) -> str | None:
    """Вернуть modifiedTime из кеша или None."""
    p = _cache_meta_path(file_id)
    if p.exists():
        try:
            with open(p, encoding="utf-8") as f:
                data = json.load(f)
            return data.get("modified_time")
        except (json.JSONDecodeError, OSError):
            pass
    return None


def _save_meta(file_id: str, meta: FileMeta, local_path: Path) -> None:
    """Сохранить метаданные в кеш."""
    dir_path = CACHE_DOWNLOADS / file_id
    dir_path.mkdir(parents=True, exist_ok=True)
    data = {
        "file_id": meta.file_id,
        "name": meta.name,
        "mime_type": meta.mime_type,
        "size": meta.size,
        "modified_time": meta.modified_time,
        "path": meta.path,
        "local_path": str(local_path),
    }
    with open(_cache_meta_path(file_id), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def download_file(
    service,
    meta: FileMeta,
    force: bool = False,
) -> Path | None:
    """
    Скачать файл в кеш. Вернуть local_path или None при ошибке.
    Не качает повторно, если modifiedTime совпадает с кешем.
    """
    cached_mtime = _cached_modified_time(meta.file_id)
    if not force and cached_mtime and cached_mtime == meta.modified_time:
        p = _cache_meta_path(meta.file_id)
        if p.exists():
            try:
                with open(p, encoding="utf-8") as f:
                    data = json.load(f)
                return Path(data.get("local_path", "")) if data.get("local_path") else None
            except (json.JSONDecodeError, OSError):
                pass

    dir_path = CACHE_DOWNLOADS / meta.file_id
    dir_path.mkdir(parents=True, exist_ok=True)

    # Расширение из имени или по MIME
    ext_map = {
        "application/pdf": ".pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "text/plain": ".txt",
        "text/markdown": ".md",
    }
    ext = Path(meta.name).suffix or ext_map.get(meta.mime_type, ".bin")
    local_path = dir_path / f"file{ext}"

    try:
        if meta.mime_type in EXPORT_MIME:
            export_mime = EXPORT_MIME[meta.mime_type]
            if "document" in meta.mime_type:
                export_mime = "text/plain"  # проще парсить текст
            content = service.files().export_media(fileId=meta.file_id, mimeType=export_mime).execute()
        else:
            content = service.files().get_media(fileId=meta.file_id).execute()

        with open(local_path, "wb") as f:
            f.write(content)
        meta.local_path = local_path
        _save_meta(meta.file_id, meta, local_path)
        return local_path
    except Exception:
        return None


def ingest(
    folder_id: str,
    credentials_path: Path,
    force: bool = False,
) -> list[FileMeta]:
    """
    Ингест: получить список файлов, скачать в кеш.
    Вернуть список FileMeta с заполненным local_path для скачанных.
    """
    ensure_cache_dirs()
    credentials_path = Path(credentials_path)
    if not credentials_path.exists():
        raise FileNotFoundError(f"Credentials not found: {credentials_path}")

    service = _get_service(credentials_path)
    files_meta: list[FileMeta] = []
    all_files = list(list_files(service, folder_id))
    file_items = [m for m in all_files if not m.is_folder]
    for meta in tqdm(file_items, desc="Скачивание", unit="файл"):
        try:
            local = download_file(service, meta, force=force)
            if local:
                meta.local_path = local
        except Exception as e:
            logger.warning("Ошибка %s: %s", meta.path, e)
        files_meta.append(meta)
    return files_meta
