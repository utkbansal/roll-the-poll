from app import app
from flask import render_template, flash, redirect, url_for, g
from forms import SignupForm, LoginForm, PollForm, VoteForm
#from werkzeug.security import generate_password_hash
from app import models, db
from flask.ext.login import login_required, login_user, logout_user, current_user
#from wtforms import ValidationError
from functools import wraps
from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib.sqla import ModelView



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
        user = models.User.query.filter_by(email=g.user).first().name
        #polls = models.Poll.query.all()
        urls = {x: str(x.body).replace(' ', '-').replace('?', '~') for x in models.Poll.query.all()}

        return render_template('content.html', user=user, url=urls)


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
        flash('Email Id Not Registered')
    return render_template('login.html', form=login_form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged Out')
    return redirect(url_for('login'))


@app.route('/profile/<int:id>')
@login_required
def profile(id):
    msg = "hello"
    if models.User.query.get(id) is not None:
        return render_template('profile.html', user=models.User.query.get(id).name)
    return render_template('profile.html', user=None, alert=msg)


@app.route('/add-poll', methods=['GET', 'POST'])
@login_required
def add_poll():
    poll_form = PollForm()
    if poll_form.validate_on_submit():
        poll = models.Poll(
            body=poll_form.poll.data,
            user_id=g.user.id,
            cat_id=poll_form.poll_category.data,
            anonymous=poll_form.anonymous.data
        )
        db.session.add(poll)
        db.session.commit()

        poll = models.Poll.query.filter_by(body=poll_form.poll.data).first()
        choice1 = models.Choice(
            poll_id=poll.id,
            value=poll_form.choice1.data
        )
        db.session.add(choice1)

        choice2 = models.Choice(
            poll_id=poll.id,
            value=poll_form.choice2.data
        )
        db.session.add(choice2)

        if str(poll_form.choice3.data) is not None and poll_form.choice3.data != '':
            choice3 = models.Choice(
                poll_id=poll.id,
                value=poll_form.choice3.data
            )
            db.session.add(choice3)

        if str(poll_form.choice4.data) is not None and poll_form.choice4.data != '':
            choice4 = models.Choice(
                poll_id=poll.id,
                value=poll_form.choice4.data
            )
            db.session.add(choice4)

        db.session.commit()
        flash('the data was', poll_form.choice3.data)
        return redirect(url_for('index'))
    return render_template('add_poll.html', form=poll_form)


@app.route('/poll/<poll>', methods=['GET', 'POST'])
@login_required
def poll(poll):
    poll = poll.replace('-', ' ')
    poll = poll.replace('~', '?')
    vote_form = VoteForm()
    voted = False
    var = models.isVoted.query.filter_by(user_id = g.user.id)
    vote_list = [x for x in var]
    if vote_list:
        for vote in vote_list:
            if vote.poll_id == models.Poll.query.filter_by(body = poll).first().id:
                voted = True
    #vote form ki choice field me choices add (to make a dynamic list for selection)
    vote_form.choice.choices = [(str(x.choice_id), str(x.value)) for x in models.Poll.query.filter_by(body = poll).first().choices.all()]
    if vote_form.validate_on_submit():
        # add a vote to the choice
        models.Choice.query.get(vote_form.choice.data).vote()
        voted = models.isVoted(
            user_id=g.user.id,
            poll_id=int(models.Poll.query.filter_by(body = poll).first().id),
            option_id = vote_form.choice.data
        )
        #update the isVoted table
        db.session.add(voted)
        comment = models.Comment(
            choice_id = vote_form.choice.data,
            user_id=g.user.id,
            body=vote_form.comment.data,
            anonymous= vote_form.anonymous.data
        )

        db.session.add(comment)

        db.session.commit()
        flash('Voted Successfully')
        return redirect('/')
    return render_template('vote.html',poll=models.Poll.query.filter_by(body=poll).first(), form = vote_form, voted=voted)
#<<<<<<< HEAD



    return render_template('vote.html',poll=models.Poll.query.filter_by(body=poll).first(), form = vote_form, voted=voted)


class MyView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin_index.html')

admin = Admin(app)

admin.add_view(ModelView(models.User, db.session))
admin.add_view(ModelView(models.Poll, db.session))
admin.add_view(ModelView(models.Choice, db.session))
admin.add_view(ModelView(models.Comment, db.session))
admin.add_view(ModelView(models.Category, db.session))
'''=======

>>>>>>> d4235001f9c59111fcd1be630daec4814f915914'''
