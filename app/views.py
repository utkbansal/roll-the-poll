from app import app
from flask import render_template, flash, redirect, url_for
from forms import SignupForm
from werkzeug.security import generate_password_hash
from app import models, db

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
