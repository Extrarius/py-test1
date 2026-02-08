"""Тест: вижу ли папку — список файлов по folder_id."""
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
FOLDER_ID = "1x6EKNkVw6PlFVTr6cGrsVscmRuwqGrXd"  # из .env GOOGLE_DRIVE_FOLDER_ID

creds = Credentials.from_authorized_user_file("token.json", SCOPES)
drive = build("drive", "v3", credentials=creds)

res = drive.files().list(
    q=f"'{FOLDER_ID}' in parents and trashed=false",
    fields="files(id,name,mimeType,modifiedTime,size)",
    supportsAllDrives=True,
    includeItemsFromAllDrives=True,
).execute()

print(f"Папка {FOLDER_ID}: {len(res.get('files', []))} элементов\n")
for f in res.get("files", []):
    print(f["name"], "|", f["mimeType"], "|", f["id"])
