from flask_wtf import FlaskForm
from wtforms import TextAreaField,  SubmitField, StringField
from wtforms.validators import Optional, Length


class DescriptionForm(FlaskForm):
    description = TextAreaField('Description', validators=[
                                Optional(), Length(0, 150)])
    submit = SubmitField()


class TagForm(FlaskForm):
    tag = StringField('Add Tag (use space sperate)',
                      validators=[Optional(), Length(0, 56)])
    submit = SubmitField()
