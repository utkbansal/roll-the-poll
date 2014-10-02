from app import app
from flask import render_template, flash, redirect, url_for, g
from forms import SignupForm, LoginForm, PollForm, VoteForm
#from werkzeug.security import generate_password_hash
from app import models, db
from flask.ext.login import login_required, login_user, logout_user, current_user
from functools import wraps
from GChartWrapper import Pie3D
from werkzeug.security import generate_password_hash, check_password_hash
# for admin
from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib.sqla import ModelView
from functools import partial
from flask.ext.admin import Admin as BaseAdmin, AdminIndexView
from flask.ext.principal import Permission,identity_loaded, Need
from flask.ext.security import current_user, url_for_security



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
    import datetime
    if g.user is not None:
        voted_polls=[x.poll_id for x in models.isVoted.query.filter_by(user_id=g.user.id)]
        polls=sorted([x for x in models.Poll.query.all()], key=lambda y: y.timestamp, reverse=True)
        poll_list=[(x, str(x.body).replace(' ', '-').replace('?', '~')) for x in polls]
        one_day=datetime.timedelta(days = 1)
        time_back=datetime.datetime.utcnow()-one_day
        recent_polls=[]
        for poll in poll_list:
            if poll[0].timestamp > time_back:
                recent_polls.append(poll)
        def vote_number(poll):
            choice_votes=[x.votes for x in poll.choices]
            votes=0
            for vote in choice_votes:
                votes+=vote
            return votes
        trending_polls=[]
        trending_dict={vote_number(p[0]): p for p in recent_polls}
        votes=sorted(trending_dict.keys(), reverse = True)
        for vote in votes:
            trending_polls.append(trending_dict[vote])
        trending_polls=trending_polls[:3]
        return render_template('content.html', voted_polls=voted_polls, poll_list=poll_list, trending=trending_polls)


@app.route('/register', methods=['GET', 'POST'])
def signup():
    signup_form=SignupForm()
    if signup_form.validate_on_submit():
        user=models.User(name=signup_form.name.data,
                                    email=signup_form.email.data,
                                    password_hash=signup_form.password.data
        )
        db.session.add(user)
        db.session.commit()

        flash('Sign Up Sucessful')
        return redirect(url_for('index'))
    return render_template('register.html', title = 'Sign Up', form=signup_form)


@app.route('/login', methods=['GET', 'POST'])
@logout_required
def login():
    login_form=LoginForm()
    if login_form.validate_on_submit() :
        user=models.User.query.filter_by(email=str(login_form.email.data)).first()
        if user is not None and user.check_password(login_form.password.data):
            login_user(user, login_form.remember_me.data)
            flash('Logged in successfully!')
            return redirect(url_for('index'))

        flash('Invalid credentials')
        redirect(url_for('login'))
    return render_template('login.html', form=login_form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    g.user = None
    flash('Logged Out')
    return redirect(url_for('login'))


@app.route('/profile/<int:id>')
@login_required
def profile(id):
    if models.User.query.get(id) is not None:
        user=models.User.query.get(id)
        is_anonymous=not(user.id==g.user.id)
        return render_template('profile.html', user=user, is_anonymous=is_anonymous )
    else:
        return render_template('profile.html', user=None)


@app.route('/add-poll', methods=['GET', 'POST'])
@login_required
def add_poll():
    poll_form=PollForm()
    if poll_form.validate_on_submit():
        poll=models.Poll(
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
    poll1=poll.replace('-', ' ')
    poll1=poll1.replace('~', '?')
    vote_form=VoteForm()
    voted=False
    var=models.isVoted.query.filter_by(user_id=g.user.id)
    vote_list=[x for x in var]
    if vote_list:
        for vote in vote_list:
            if vote.poll_id==models.Poll.query.filter_by(body=poll1).first().id:
                voted=True
    #vote form ki choice field me choices add (to make a dynamic list for selection)
    vote_form.choice.choices=[(str(x.choice_id), str(x.value)) for x in models.Poll.query.filter_by(body=poll1).first().choices.all()]

    #adding pie chart
    c=[x for x in models.Poll.query.filter_by(body=poll1).first().choices]
    choice_vote=[['choice', 'votes']]
    for choice in c:
        choice_vote.append([str(choice), int(choice.votes)])

    if vote_form.validate_on_submit():
        # add a vote to the choice
        models.Choice.query.get(vote_form.choice.data).vote()
        voted=models.isVoted(
            user_id=g.user.id,
            poll_id=int(models.Poll.query.filter_by(body=poll1).first().id),
            option_id=vote_form.choice.data
        )

        #update the isVoted table
        db.session.add(voted)

        if vote_form.comment.data is not None and vote_form.comment.data != '':
            comment=models.Comment(
                choice_id=vote_form.choice.data,
                user_id=g.user.id,
                body=vote_form.comment.data,
                anonymous=vote_form.anonymous.data
            )
            db.session.add(comment)
        db.session.commit()
        flash('Voted Successfully')
        return redirect(url_for('poll',poll=poll))
    return render_template('vote.html',poll=models.Poll.query.filter_by(body=poll1).first(), form=vote_form, voted=voted, choice_vote=choice_vote)


#implementing view of the polls in which user has participated
@app.route('/participated')
@login_required
def polls_participated():
    user=models.User.query.get(g.user.id)
    polls=[models.Poll.query.get(x) for x in models.isVoted.query.filter_by(user_id=g.user.id)]
    return render_template('participated.html', user=user, polls=polls)


# admin


class MyView(ModelView):
    pass
    '''    def __init__(self,User, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(MyUserView, self).__init__(User, session, **kwargs)


    @expose('/admin')
    def index(self):
        return self.render('admin_index.html')'''


admin=Admin(app)

'''    def is_accessible(self):
        if current_user:
            return g.user.id == 1
        return False
'''

class MyAdminIndexView(AdminIndexView, BaseView, BaseAdmin):

    def is_accessible(self):
        return False

admin = Admin(app)
#admin.add_view(MyView(url=url_for('.index')))
admin.add_view(MyView(models.User, db.session))
admin.add_view(MyView(models.Poll, db.session))
admin.add_view(MyView(models.Choice, db.session))
admin.add_view(MyView(models.Comment, db.session))
admin.add_view(MyView(models.Category, db.session))
