from app import app
from flask import render_template, flash, redirect, url_for, g
from forms import SignupForm, LoginForm
from werkzeug.security import generate_password_hash
from app import models, db
from flask.ext.login import login_required, login_user, logout_user, current_user
from wtforms import ValidationError
from functools import wraps


def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user.is_authenticated():
            #raise ValidationError('You are already logged in')
            flash('You are already logged in')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def before_request():
    g.user = current_user

@app.route('/')
@login_required
def index():
    if g.user is not None:
        user = models.User.query.filter_by(email = g.user).first().name
        polls = models.Poll.query.all()
        return render_template('content.html', user = user, polls = polls)


@app.route('/register', methods=['GET', 'POST'])
def signup():
    signup_form = SignupForm()
    if signup_form.validate_on_submit():
        user = models.User(name = signup_form.name.data,
                                    email = signup_form.email.data,
                                    password_hash = signup_form.password.data
        )
        db.session.add(user)
        db.session.commit()

        flash('Sign Up Sucessful')
        return redirect(url_for('index'))
    return render_template('register.html', title='Sign Up', form=signup_form)


@app.route('/login', methods=['GET', 'POST'])
@logout_required
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit() and models.User.query.filter_by(email=str(login_form.email.data)).first() is not None:
        password = str(models.User.query.filter_by(email=str(login_form.email.data)).first().password_hash)
        if password == str(login_form.password.data):
            login_user(models.User.query.filter_by(email=login_form.email.data).first(), remember=login_form.remember_me.data)
            flash('Hi User')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials')
            redirect(url_for('login'))
    if models.User.query.filter_by(email=str(login_form.email.data)).first():
        flash('Emain Id Not Registered')
    return render_template('login.html', form=login_form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged Out')
    return redirect(url_for('login'))



