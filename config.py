"""Application configuration.

All environment-specific settings live here so secrets and paths
are never hard-coded inside the application package.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Base configuration shared by every environment."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    # POSIX slashes work on Windows too, so the SQLite URI stays valid.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + (BASE_DIR / "instance" / "psr.db").as_posix(),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Upload settings (optional request photos) ---
    UPLOAD_FOLDER = BASE_DIR / "uploads"
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024            # reject uploads > 5 MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}