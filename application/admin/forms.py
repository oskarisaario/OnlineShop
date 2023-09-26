from wtforms import Form, StringField, PasswordField, validators, ValidationError
from flask_wtf import FlaskForm

from .models import User


class RegistrationForm(FlaskForm):
    name = StringField('Name', [validators.Length(min=4, max=25)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35),validators.email()])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

    #Checks if Username/Email is already in database and raises error!
    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError("This username is already in use!")


    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError("This email is already in use!")


class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.DataRequired()])