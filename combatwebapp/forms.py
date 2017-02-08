from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, ValidationError


class SearchForm(FlaskForm):
    search = StringField('Search for gene...', validators=[DataRequired()])


class LoginForm(FlaskForm):
    email = EmailField('Enter your email', validators=[DataRequired(), Email('your@email.com')])
    password = PasswordField('Enter your password', validators=[DataRequired()])


class RegisterForm(FlaskForm):
    username = StringField('Enter username', validators=[DataRequired()])
    email = EmailField('Enter your email', validators=[DataRequired(), Email('your@email.com')])
    password = PasswordField('Enter your password', validators=[DataRequired()])
    _password = PasswordField('Confirm password', validators=[DataRequired()])

    def __init__(self):
        FlaskForm.__init__(self)
        if self.password is not self._password:
            raise ValidationError('Password do not match, please try again.')
