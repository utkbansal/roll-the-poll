from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, SubmitField, BooleanField,ValidationError, TextAreaField, SelectField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, Optional
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

class PollForm(Form):
    poll = TextAreaField('Poll', validators=[DataRequired()])
    choice1 = StringField('Choice 1', validators=[DataRequired()])
    choice2 = StringField('Choice 2', validators=[DataRequired()])
    choice3 = StringField('Choice 3',validators=[Optional()])
    choice4 = StringField('Choice 4', validators=[Optional()])
    poll_category = SelectField('Category', choices = [(str(x.id), str(x.name)) for x in models.Category.query.order_by('name')])
    anonymous = BooleanField('Anonymous')
    submit = SubmitField('Submit')

class VoteForm(Form):
    choice = RadioField('Select')
    comment = TextAreaField('Comment', validators=[Optional()])
    submit = SubmitField('Poll')
    anonymous = BooleanField('Anonymous')