from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, SubmitField, BooleanField,ValidationError
from wtforms.validators import DataRequired, Email, EqualTo
from app import models


class SignupForm(Form):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email ID', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2', message='Passwords do not match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_email(self, field):
        if models.User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

class LoginForm(Form):
    email = StringField('Name', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log in')

    def validate_email(self, field):
        if models.User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Email not registered.')