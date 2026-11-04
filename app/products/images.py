from pathlib import Path
from uuid import uuid4

from flask import current_app
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = Path(__file__).resolve().parent / "static" / "uploads"
MAX_IMAGE_SIZE = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}


def save_image(file):
    if file is None or not file.filename:
        return None

    filename = secure_filename(file.filename)
    extension = Path(filename).suffix.lower().lstrip(".")

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Недопустимий формат зображення")

    file.stream.seek(0, 2)
    size = file.stream.tell()
    file.stream.seek(0)

    if size > MAX_IMAGE_SIZE:
        raise RequestEntityTooLarge(
            description="Розмір зображення не може перевищувати 5 МБ"
        )

    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    unique_filename = f"{uuid4().hex}.{extension}"
    file.save(UPLOAD_FOLDER / unique_filename)

    return unique_filename


def delete_image(filename):
    if not filename:
        return

    path = UPLOAD_FOLDER / Path(filename).name

    if path.is_file():
        path.unlink()
