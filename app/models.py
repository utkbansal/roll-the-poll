from app import db, login_manager
from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import string
import datetime

#user class
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True) #primary key
    name = db.Column(db.String(150), index = True, nullable = False)
    email = db.Column(db.String(150), unique = True, nullable = False)
    password_hash = db.Column(db.String(128), nullable = False)#hashed_password
    polls = db.relationship("Poll", backref = "creator", lazy = "dynamic")
    voted = db.relationship("isVoted", backref = "voter", lazy = "dynamic")
    comments = db.relationship("Comment", backref = "commenter", lazy = "dynamic")
	
    def __repr__(self):
        return self.email

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    def __init__(self, name, email, password_hash):
        self.name = name
        self.email = email
        self.set_password(password_hash)

    def set_password(self, password_hash):
        self.password_hash = generate_password_hash(password_hash)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

#poll class
class Poll(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.Text(1000), nullable = False)
    timestamp = db.Column(db.DateTime, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    cat_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable = False)
    anonymous = db.Column(db.Boolean, nullable = False)
    choices = db.relationship("Choice", backref = "poll", lazy = "dynamic")
    users_voted = db.relationship("isVoted", backref = "polled", lazy = "dynamic")
    def __init__(self, body, user_id, cat_id, anonymous):
        
        self.timestamp = datetime.datetime.utcnow()
        self.id = id
        self.body = body
        self.user_id = user_id
        self.cat_id = cat_id
        self.anonymous = anonymous

    def __repr__(self):
        return self.body

#category class
class Category(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(150), unique = True, index = True, nullable = False)
    polls = db.relationship("Poll", backref = "category", lazy = "dynamic")

    def __repr__(self):
        return self.name

#Choice class
class Choice(db.Model):
    alphabets = string.ascii_lowercase
    poll_id_dict = {}
    poll_id = db.Column(db.Integer, db.ForeignKey("poll.id"), nullable = False)
    choice_id = db.Column(db.String(10), primary_key = True)
    value = db.Column(db.String(100), index = True, nullable = False)
    votes = db.Column(db.Integer, nullable = False)
    comments = db.relationship("Comment", backref = "choice", lazy = "dynamic")
    user_voted = db.relationship("isVoted", backref = "user_choice", lazy = "dynamic")

    def __init__(self, poll_id, value):
        if poll_id not in Choice.poll_id_dict.keys():
            Choice.poll_id_dict[poll_id] = 0

        self.poll_id = poll_id
        self.choice_id = self.generate_id(poll_id)
        self.value = value
        self.votes = 0
 

    def generate_id(self, poll_id):
        '''
        generates id for Choice in the format 1a, 2c etc.
        '''
        id = str(poll_id) + Choice.alphabets[Choice.poll_id_dict[poll_id]]
        Choice.poll_id_dict[poll_id] += 1
        return id

    def vote(self):
        '''
        increases the vote count by one
        '''
        self.votes += 1

    def __repr__(self):
        return self.value

#comment class
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    #comment choice id is c_choice_id
    c_choice_id = db.Column(db.String(10), db.ForeignKey("choice.choice_id"), nullable = False)
    body = db.Column(db.Text(200), nullable = False)
    timestamp = db.Column(db.DateTime, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    anonymous = db.Column(db.Boolean, nullable = False)

    def __init__(self, body, choice_id, user_id, anonymous = False):
        self.body = body
        self.c_choice_id = choice_id#comment Choice id
        self.user_id = user_id
        self.anonymous = anonymous
        self.timestamp = datetime.datetime.utcnow()

    def __repr__(self):
        return self.body

#voted class
class isVoted(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    poll_id = db.Column(db.Integer, db.ForeignKey("poll.id"), nullable=False)
    option_id = db.Column(db.String(10), db.ForeignKey("choice.choice_id"), nullable=False)

    def __repr__(self):
        return str(self.poll_id)

# Admin class
class Admin(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return self.id