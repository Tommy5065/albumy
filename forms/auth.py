from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp
from albumy.models import User

class RegisterForm(FlaskForm):
    Name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    Email = EmailField('Email', validators=[DataRequired(), Length(1, 254), Email()])
    Username = StringField('Username', validators=[DataRequired(), Length(1, 20), Regexp('^[a-zA-Z0-9]*$',message='The username should contain only a-z, A-Z and 0-9')])
    Password = PasswordField('Password', validators=[DataRequired(), Length(8, 256), EqualTo('Password2')])
    Password2 = PasswordField('Confirm Password', validators=[DataRequired(), Length(8, 256)])
    Submit = SubmitField('Submit')

    def validate_email(self, field):
        if User.query.filter(field.Email.data):
            raise ValidationError('The Email has already in use')

    def validate_username(self,field):
        if User.query.filter(field.Username.data):
            raise ValidationError('The username has already exist')
