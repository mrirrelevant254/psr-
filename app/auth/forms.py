"""WTForms forms for authentication.

First install the e-mail validator:  pip install email_validator
"""
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from app.models import User


class RegisterForm(FlaskForm):
    """Citizen sign-up form."""

    full_name = StringField("Full name", validators=[DataRequired(), Length(max=80)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=6, message="use at least 6 characters.")],
    )
    confirm = PasswordField(
        "Confirm password",
        validators=[DataRequired(), EqualTo("password", message="passwords must match.")],
    )
    submit = SubmitField("Create account")

    def validate_email(self, field):
        """Custom validator: reject e-mails that are already registered."""
        if User.query.filter_by(email=field.data.strip().lower()).first():
            raise ValidationError("that e-mail is already registered, log in instead.")


class LoginForm(FlaskForm):
    """Login form for citizens and admins."""

    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in")