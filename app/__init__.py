import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "psr-secret-key-change-me"
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        base_dir, "..", "instance", "psr.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        # --- Upload settings (optional request photos) ---
    app.config["UPLOAD_FOLDER"] = os.path.join(base_dir, "..", "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024   # reject files > 5 MB
    app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "webp"}
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)

    from app.admin.routes import admin_bp
    from app.citizen.routes import citizen_bp

    app.register_blueprint(citizen_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.errorhandler(403)
    def forbidden(_e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(_e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(413)
    def file_too_large(_e):
        return render_template("errors/413.html"), 413

    with app.app_context():
        from app import models  # noqa: F401

        db.create_all()

    return app