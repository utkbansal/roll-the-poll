from app import app
from flask import render_template, flash, redirect, url_for
from forms import SignupForm, LoginForm
from werkzeug.security import generate_password_hash
from app import models, db
from flask.ext.login import login_required, login_user, logout_user


@app.route('/')
@app.route('/index')
def index():
    return render_template('base.html')


@app.route('/signup', methods=['GET', 'POST'])
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
    return render_template('signup.html', title='Sign Up', form=signup_form)


@app.route('/login', methods=['GET', 'POST'])
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
    return redirect(url_for('index'))


@app.route('/secret')
@login_required
def secret():
    return render_template('secret.html')


