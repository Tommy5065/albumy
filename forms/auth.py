from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    email = EmailField('Email', validators=[DataRequired(), Length(1, 254), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(1, 20), Regexp('^[a-zA-Z0-9]*$',message='The username should contain only a-z, A-Z and 0-9')])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 256), EqualTo('password2')])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), Length(8, 256)])
    submit = SubmitField('Submit')

    def validate_email(self, field):
        from albumy.models import User
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('The Email has already in use')

    def validate_username(self, field):
        from albumy.models import User
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('The username has already exist')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Length(1,254), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(8,256)])
    remember_Me = BooleanField('Remember Me')
    submit = SubmitField('login in')

class ForgetPasswordForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Length(1, 254), Email()])
    submit = SubmitField()

class ResetPasswordForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Length(1,254), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 256), EqualTo('password2')])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), Length(8, 256)])
    submit = SubmitField()