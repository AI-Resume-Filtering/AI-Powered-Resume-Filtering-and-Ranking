import os
import uuid
from pathlib import Path
from werkzeug.utils import secure_filename


class StorageService:
    def __init__(self, uploads_dir: str, tmp_dir: str):
        self.uploads_dir = uploads_dir
        self.tmp_dir = tmp_dir
        Path(self.uploads_dir).mkdir(parents=True, exist_ok=True)
        Path(self.tmp_dir).mkdir(parents=True, exist_ok=True)

    def save_upload(self, file_storage, subdir: str) -> str:
        if file_storage is None:
            raise ValueError("No file provided")

        safe_name = secure_filename(file_storage.filename or "upload.bin")
        unique_prefix = uuid.uuid4().hex
        target_dir = Path(self.uploads_dir) / subdir
        target_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{unique_prefix}_{safe_name}"
        target_path = target_dir / filename
        file_storage.save(str(target_path))
        return str(target_path)

    def write_text(self, text: str, filename: str) -> str:
        target_path = Path(self.tmp_dir) / filename
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as file_obj:
            file_obj.write(text or "")
        return str(target_path)
