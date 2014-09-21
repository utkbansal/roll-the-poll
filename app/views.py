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
    
@app.route('/signup', methods = ['GET','POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        user = models.User(name = form.name.data,
                                    email = form.email.data,
                                    password_hash = form.password.data
        )
        db.session.add(user)
        db.session.commit()

        flash('Sign Up Sucessful')
        return redirect(url_for('index'))
    return render_template('signup.html', title = 'Sign Up', form = form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = str(models.User.query.filter_by(email = str(form.email.data)).first().password_hash)
        if password == str(form.password.data):
            login_user(models.User.query.filter_by(email = form.email.data).first(), form.remember_me.data)
            flash('Hi User')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials')
            redirect(url_for('login'))
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged Out')
    return redirect(url_for('index'))





