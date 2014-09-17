from app import app
from flask import render_template, flash, redirect, url_for
from forms import SignupForm 


@app.route('/')
@app.route('/index')
def index():
    return render_template('base.html')
    
@app.route('/signup', methods = ['GET','POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        flash('Sign Up Sucessful')
        return redirect(url_for('index'))
    return render_template('signup.html', title = 'Sign Up', form = form)
