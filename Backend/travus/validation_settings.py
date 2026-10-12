"""Isolated SQLite settings for accessibility checks; never loads project .env."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "local-accessibility-validation-only"
DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
INSTALLED_APPS = [
    "django.contrib.auth", "django.contrib.contenttypes", "django.contrib.sessions",
    "rest_framework", "corsheaders", "accounts", "api",
]
MIDDLEWARE = ["corsheaders.middleware.CorsMiddleware"]
CORS_ALLOWED_ORIGINS = ["http://127.0.0.1:5173", "http://localhost:5173"]
DATABASES = {"default": {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": os.environ.get("TRAVUS_VALIDATION_DB", str(BASE_DIR / "accessibility_validation.sqlite3")),
}}
AUTH_USER_MODEL = "accounts.User"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
ROOT_URLCONF = "travus.validation_urls"
USE_TZ = True
TIME_ZONE = "Asia/Seoul"
REST_FRAMEWORK = {"DEFAULT_AUTHENTICATION_CLASSES": [], "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"]}
TOUR_API_BASE_URL = "https://apis.data.go.kr/B551011/KorWithService2"
TOUR_API_KEY = ""
TOUR_API_MOBILE_OS = "ETC"
TOUR_API_MOBILE_APP = "TravUsValidation"
GMS_API_KEY = ""
