from flask_wtf import FlaskForm
from wtforms import TextAreaField,  SubmitField
from wtforms.validators import Optional, Length


class DescriptionForm(FlaskForm):
    description = TextAreaField('Description', validators=[
                                Optional(), Length(0, 150)])
    submit = SubmitField()
