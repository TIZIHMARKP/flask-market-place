from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField


class RegisterForm(FlaskForm):     # It basically kind of gives a secondary title for our fields

    username = StringField(label='User Name: ')
    email_address = StringField(label = 'Email Address: ')
    password1 = PasswordField(label = 'Password')
    password2 = PasswordField(label = 'Confirm Password')
    submit = SubmitField(label = 'Create Account')



