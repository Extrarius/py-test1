"""Google Drive API — источник файлов."""
from pathlib import Path
from typing import Any

from src.config import GOOGLE_CREDENTIALS_PATH, PROJECT_ROOT
from src.sources.base import BaseSource
from src.sources.drive_api import ingest as drive_ingest
from src.sources.models import FileMeta


class DriveSource(BaseSource):
    """Источник: Google Drive API."""

    def __init__(self, credentials_path: Path | str | None = None):
        self.credentials_path = Path(
            credentials_path or PROJECT_ROOT / GOOGLE_CREDENTIALS_PATH
        )

    def ingest(
        self,
        *,
        folder_id: str | None = None,
        path: Path | str | None = None,
        force: bool = False,
        **kwargs: Any,
    ) -> list[FileMeta]:
        """Скачать файлы из папки Drive, вернуть FileMeta с local_path."""
        from src.config import GOOGLE_DRIVE_FOLDER_ID

        fid = folder_id or kwargs.get("folder_id") or GOOGLE_DRIVE_FOLDER_ID
        return drive_ingest(fid, self.credentials_path, force=force)
