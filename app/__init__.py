"""Application factory.

Keeps configuration, extension init and blueprint registration in one
readable place, and makes the app easy to test.
"""
from flask import Flask

from config import BASE_DIR, Config
from app.extensions import csrf, db, login_manager


def create_app(config_class=Config) -> Flask:
    """Create and fully configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Make sure runtime folders exist (safe on every OS).
    (BASE_DIR / "instance").mkdir(parents=True, exist_ok=True)
    app.config["UPLOAD_FOLDER"].mkdir(parents=True, exist_ok=True)

    # Extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
        # Expose the status -> badge colour mapping to every template.
    from app.utils import badge_class
    app.jinja_env.globals["badge_class"] = badge_class

    # Blueprints (one per role)
    from app.auth.routes import auth_bp
    from app.citizen.routes import citizen_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(auth_bp)                        # /login, /register
    app.register_blueprint(citizen_bp)                     # /, /requests/...
    app.register_blueprint(admin_bp, url_prefix="/admin")  # /admin/...

    # Flask-Login: load the user object from the session id.
    from app.models import User, UserRole

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))

    # Dev convenience: create tables on first run.
    with app.app_context():
        db.create_all()

    # ---------------------------------------------------------- CLI tooling
    @app.cli.command("create-admin")
    def create_admin():
        """Create/promote an admin (run:  flask --app run create-admin)."""
        import click

        email = click.prompt("Admin e-mail").strip().lower()
        existing = User.query.filter_by(email=email).first()
        if existing:
            if existing.is_admin:
                click.echo("That user is already an admin.")
            else:
                existing.role = UserRole.ADMIN
                db.session.commit()
                click.echo(f"Promoted {email} to admin.")
            return
        name = click.prompt("Full name", default="Administrator")
        password = click.prompt("Password", hide_input=True, confirmation_prompt=True)
        admin = User(full_name=name, email=email, role=UserRole.ADMIN)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        click.echo(f"Admin '{email}' created.")

    return app