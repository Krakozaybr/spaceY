import os

APP_NAME = "SpaceY"
BASE_DIR = os.path.dirname(__file__)
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
MEDIA_DIR = os.path.join(STATIC_DIR, "media")
DB_NAME = "db.sqlite"
DB_DIR = os.path.join(BASE_DIR, "db")
DB_FILE = os.path.join(DB_DIR, DB_NAME)

STATIC_IMAGES_DIR_NAME = "images"
STATIC_IMAGES_DIR = os.path.join(STATIC_DIR, STATIC_IMAGES_DIR_NAME)

MEDIA_IMAGES_DIR_NAME = "images"
MEDIA_IMAGES_DIR = os.path.join(MEDIA_DIR, MEDIA_IMAGES_DIR_NAME)
MEDIA_VIDEOS_DIR_NAME = "videos"
MEDIA_VIDEOS_DIR = os.path.join(MEDIA_DIR, MEDIA_VIDEOS_DIR_NAME)

MEDIA_IMAGES_URL_DIR = 'media/images'
MEDIA_VIDEOS_URL_DIR = os.path.join('media', MEDIA_VIDEOS_DIR_NAME)

ALLOWED_IMAGES_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
ALLOWED_VIDEO_EXTENSIONS = {"mp4"}

AUTH_KEY = "SpaceY-access"
