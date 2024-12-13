"""
Form module for new cert creation
"""

from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, RadioField, StringField, TextAreaField, validators


class CertForm(FlaskForm):
    """
    Defines a form for creating a new cert
    """
    name = StringField("Name", validators=[validators.DataRequired()])
    code = StringField("Code", validators=[validators.DataRequired()])
    tags = StringField("Tags", validators=[validators.DataRequired()])
    head_img = StringField(
        "Image path",
        validators=[validators.DataRequired()]
    )
    badge_img = StringField(
        "Badge path",
        validators=[validators.DataRequired()]
    )
    exam_date = StringField("Exam date")


class ResourceForm(FlaskForm):
    """
    Defines a form for adding resources to a cert
    """
    resource_type = RadioField("Resource type", choices=[
        ("course", "Course"),
        ("video", "Video"),
        ("article", "Article"),
        ("documentation", "Documentation")],
        validators=[validators.DataRequired()],
    )
    url = StringField("URL", validators=[validators.DataRequired()])
    title = StringField("Title", validators=[validators.DataRequired()])
    image = StringField("Image")
    description = StringField(
        "Description",
        validators=[validators.DataRequired()]
    )
    site_logo = StringField("Site logo")
    site_name = StringField(
        "Site name",
        validators=[validators.DataRequired()]
    )


class SectionForm(FlaskForm):
    """
    Defines a form for adding a section to a course
    """
    number = StringField(
        "Section number",
        validators=[validators.DataRequired()]
    )
    title = StringField("Title", validators=[validators.DataRequired()])
    cards_made = BooleanField("Flash cards", default=False)
    complete = BooleanField("Complete", default=False)


class SectionImportForm(FlaskForm):
    """
    Defines a form for importing sections as JSON
    """
    text_area = TextAreaField(
        "Section data JSON",
        validators=[validators.DataRequired()]
    )


class EmailReminderForm(FlaskForm):
    """
    Defines a form for configuring email reminders
    """
    frequency = RadioField("Frequency", choices=[
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly")],
        validators=[validators.DataRequired()],
    )
    starting_from = DateField("Starting date", format="%d-%m-%Y")
