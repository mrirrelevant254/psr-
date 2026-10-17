"""Flask extension instances.

Created here (outside the app factory) so models and blueprints can
import them without circular-import problems.
"""
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

# Where Flask-Login sends anonymous users who hit a protected route.
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"