import os
import uuid
from typing import Iterable

from flask import url_for

import settings


def get_extension(filename: str):
    return filename.rsplit(".", 1)[1].lower()


def allowed_file(filename: str, allowed_extensions: Iterable[str]) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


class ImageFormatException(Exception):
    pass


class VideoFormatException(Exception):
    pass


def save_media(data, dest_dir) -> str:
    filename = str(uuid.uuid4())
    while os.path.exists(filename):
        filename = str(uuid.uuid4())

    filename += "." + get_extension(data.filename)
    data.save(os.path.join(dest_dir, filename))

    return filename


def delete_media(name: str, dest_dir: str):
    way = os.path.join(dest_dir, name)
    if os.path.exists(way):
        os.remove(way)


def save_video(data):
    if not allowed_file(data.filename, settings.ALLOWED_VIDEO_EXTENSIONS):
        raise VideoFormatException
    return save_media(data, settings.MEDIA_VIDEOS_DIR)


def delete_video(filename: str):
    delete_media(filename, settings.MEDIA_VIDEOS_DIR)


def save_image(data):
    if not allowed_file(data.filename, settings.ALLOWED_IMAGES_EXTENSIONS):
        raise ImageFormatException
    return save_media(data, settings.MEDIA_IMAGES_DIR)


def delete_img(filename: str):
    delete_media(filename, settings.MEDIA_IMAGES_DIR)


def media_img_url(img_name: str):
    return url_for("static", filename=f'{settings.MEDIA_IMAGES_URL_DIR}/{img_name}')


def static_img_url(img_name: str):
    return url_for("static", filename=f'{settings.STATIC_IMAGES_DIR_NAME}/{img_name}')
