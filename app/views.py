from app import app
from flask import render_template, flash, redirect, url_for, g
from forms import SignupForm, LoginForm, PollForm, VoteForm
#from werkzeug.security import generate_password_hash
from app import models, db
from flask.ext.login import login_required, login_user, logout_user, current_user
from functools import wraps
from GChartWrapper import Pie3D
from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash, check_password_hash



#creating the @logout_required decorator
def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user.is_authenticated():
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
        polls = sorted([x for x in models.Poll.query.all()], key = lambda y: y.timestamp, reverse = True)
        urls = [(x, str(x.body).replace(' ', '-').replace('?', '~')) for x in polls]

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
    if login_form.validate_on_submit() :
        user = models.User.query.filter_by(email=str(login_form.email.data)).first()
        if user is not None and user.check_password(login_form.password.data):
            login_user(user, login_form.remember_me.data)
            flash('Hi User')
            return redirect(url_for('index'))

        flash('Invalid credentials')
        redirect(url_for('login'))
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
    if models.User.query.get(id) is not None:
        user = models.User.query.get(id)
        anonymous = not(user.id == g.user.id)
        return render_template('profile.html', user= user, anonymous = anonymous )
    else:
        return render_template('profile.html', user=None)


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

    #adding pie chart
    c = [x for x in models.Poll.query.filter_by(body = poll).first().choices]
    v = [int(x.votes) for x in models.Poll.query.filter_by(body=poll).first().choices]
    chart = str(Pie3D(v).color('red', 'green', 'blue', 'yellow'))

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

        if vote_form.comment.data is not None and vote_form.comment.data != '':
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
    return render_template('vote.html',poll=models.Poll.query.filter_by(body=poll).first(), form = vote_form, voted=voted, chart=chart)



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
