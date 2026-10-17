"""WTForms form for submitting a service request."""
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

from app.models import RequestCategory


class RequestForm(FlaskForm):
    """Category + location + description, with an optional photo."""

    category = SelectField(
        "Category",
        choices=[(c, c) for c in RequestCategory.ALL],
        validators=[DataRequired()],
    )
    location = StringField(
        "Location",
        validators=[DataRequired(), Length(max=120)],
        render_kw={"placeholder": "e.g. Kenyatta Ave, near the market"},
    )
    description = TextAreaField(
        "Description",
        validators=[DataRequired(), Length(max=2000)],
        render_kw={"rows": 4, "placeholder": "Describe the issue..."},
    )
    # A FileField with only FileAllowed is optional; adding FileRequired()
    # would make the photo mandatory.
    image = FileField(
        "Photo (optional)",
        validators=[
            FileAllowed(["png", "jpg", "jpeg", "webp"], "Images only (png/jpg/webp)."),
        ],
    )
    submit = SubmitField("Submit request")