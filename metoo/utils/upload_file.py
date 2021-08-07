import shutil
import uuid
import os
from typing import Optional

from fastapi import UploadFile

from core.config import settings


def save_upload_file(upload_file: UploadFile, *, sub_folder: Optional[str]) -> str:
    try:
        if sub_folder:
            dirs = f"{settings.UPLOAD_FOLDER}/{sub_folder}"
        else:
            dirs = f"{settings.UPLOAD_FOLDER}"

        if not os.path.exists(dirs):
            os.makedirs(dirs)

        file_location = f"{dirs}/{uuid.uuid1()}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()

    return file_location
