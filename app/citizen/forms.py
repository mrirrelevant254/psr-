from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (PasswordField, SelectField, StringField, SubmitField,
                     TextAreaField)
from wtforms.validators import DataRequired, Length, ValidationError

from app.models import RequestCategory, SubCounty

IMAGE_EXTENSIONS = ["png", "jpg", "jpeg", "webp"]


class RegisterForm(FlaskForm):
    full_name = StringField("Full name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class RequestForm(FlaskForm):
    category = SelectField(
        "Category", choices=[(c, c) for c in RequestCategory.ALL],
        validators=[DataRequired()],
    )
    sub_county = SelectField(
        "Sub-County", choices=[(s, s) for s in SubCounty.ALL],
        validators=[DataRequired()],
    )
    location = StringField("Location", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Description", validators=[DataRequired(), Length(max=2000)])

    image = FileField(
        "Photo (optional)",
        validators=[FileAllowed(IMAGE_EXTENSIONS,
                                "Only image files are allowed (PNG, JPG, JPEG, WEBP).")],
    )
    submit = SubmitField("Submit request")

    def validate_image(self, field):
        """Server-side proof the upload is really an image.

        1) MIME type must start with 'image/'.
        2) The first bytes (magic numbers) must match PNG / JPEG / WEBP,
           so a renamed .exe or .txt is rejected even if its extension lies.
        """
        if field.data is None or not field.data.filename:
            return                                    
        if not (field.data.mimetype or "").startswith("image/"):
            raise ValidationError("Only image files are allowed.")
        header = field.data.stream.read(12)
        field.data.stream.seek(0)                     
        is_png = header[:4] == b"\x89PNG"
        is_jpg = header[:3] == b"\xff\xd8\xff"
        is_webp = header[:4] == b"RIFF" and header[8:12] == b"WEBP"
        if not (is_png or is_jpg or is_webp):
            raise ValidationError("File content is not a valid PNG, JPG or WEBP image.")