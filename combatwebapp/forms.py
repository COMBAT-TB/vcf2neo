from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email


class LoginForm(FlaskForm):
    email = EmailField('Enter your email', validators=[DataRequired(), Email('your@email.com')])
    password = PasswordField('Enter your password', [])
