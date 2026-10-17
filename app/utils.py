"""Small shared helpers used across blueprints."""
from datetime import datetime, timezone
from pathlib import Path

from flask import current_app, flash
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename

from app.models import RequestStatus


def flash_form_errors(form: FlaskForm) -> None:
    """Flash every WTForms field error as a Bootstrap 'danger' alert."""
    for field_name, errors in form.errors.items():
        for error in errors:
            label = getattr(form, field_name).label.text
            flash(f"{label}: {error}", "danger")


# ------------------------------------------------------------------ uploads
def allowed_file(filename: str) -> bool:
    """True when the upload's extension is in the configured allow-list."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]
    )


def save_image(file_storage) -> str | None:
    """Persist an uploaded photo in uploads/ and return its safe filename.

    Returns None when nothing was uploaded (the photo is optional).
    A timestamp prefix prevents two users overwriting each other's files.
    """
    if file_storage is None or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename):
        return None
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
    safe_name = f"{stamp}_{secure_filename(file_storage.filename)}"
    file_storage.save(Path(current_app.config["UPLOAD_FOLDER"]) / safe_name)
    return safe_name


# --------------------------------------------------------------- UI helpers
STATUS_BADGE_CLASSES = {
    RequestStatus.PENDING: "text-bg-warning",
    RequestStatus.IN_PROGRESS: "text-bg-primary",
    RequestStatus.RESOLVED: "text-bg-success",
}


def badge_class(status: str) -> str:
    """Bootstrap badge colour for a workflow status (used in templates)."""
    return STATUS_BADGE_CLASSES.get(status, "text-bg-secondary")