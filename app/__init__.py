"""Application factory. Keeps configuration, extension init, and blueprint registration clean."""
import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    
    # --- Core Configuration ---
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "psr-secret-key-change-me")
    
    # --- Detect Vercel Environment ---
    is_vercel = os.environ.get("VERCEL") == "1"
    
    if is_vercel:
        # Vercel uses /tmp for writable files
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/psr.db"
        app.config["UPLOAD_FOLDER"] = "/tmp/uploads"
    else:
        # Local fallback for your computer
        base_dir = os.path.abspath(os.path.dirname(__file__))
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(base_dir, "..", "instance", "psr.db")
        app.config["UPLOAD_FOLDER"] = os.path.join(base_dir, "..", "uploads")

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024   # reject files > 5 MB
    app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "webp"}
    
    # Create folders safely
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    if not is_vercel:
        os.makedirs(os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "instance"), exist_ok=True)

    db.init_app(app)

    # --- Register Blueprints ---
    from app.citizen.routes import citizen_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(citizen_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # --- Error Handlers ---
    @app.errorhandler(403)
    def forbidden(_e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(_e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(413)
    def file_too_large(_e):
        return render_template("errors/413.html"), 413

    # --- Database Initialization ---
    with app.app_context():
        from app import models  # noqa: F401
        db.create_all()

    return app