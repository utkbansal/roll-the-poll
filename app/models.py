from app import db, login_manager
from flask.ext.login import UserMixin
#from warkzeag.security import generate_password_hash, check_password_hash
import string
import datetime

#user table
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(150), index = True, nullable = False)
    email = db.Column(db.String(150), unique = True, nullable = False)
    password_hash = db.Column(db.String(128), nullable = False)#hashed_password
    polls = db.relationship("Poll", backref = "creator", lazy = "dynamic")
	
    def __repr__(self):
        return self.email

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

#poll table
class Poll(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.Text(1000), nullable = False)
    timestamp = db.Column(db.DateTime, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    cat_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable = False)
    anonymous = db.Column(db.Boolean, nullable = False)
    options = db.relationship("Option", backref = "poll", lazy = "dynamic")
    def __init__(self, body, user_id, cat_id, anonymous):
        
        self.timestamp = datetime.datetime.utcnow()
        self.id = id
        self.body = body
        self.user_id = user_id
        self.cat_id = cat_id
        self.anonymous = anonymous

    def __repr__(self):
        return self.body

#category table
class Category(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(150), unique = True, index = True, nullable = False)
    polls = db.relationship("Poll", backref = "poll", lazy = "dynamic")

    def __repr__(self):
        return self.name

#option table
class Option(db.Model):
    alphabets = string.ascii_lowercase
    poll_id_dict = {}
    poll_id = db.Column(db.Integer, db.ForeignKey("poll.id"), nullable = False)
    option_id = db.Column(db.String(10), primary_key = True)
    value = db.Column(db.String(100), index = True, nullable = False)
    count = db.Column(db.Integer, nullable = False)
    comments = db.relationship("Comment")


    def __init__(self, poll_id, value):
        if poll_id not in Option.poll_id_dict.keys():
            Option.poll_id_dict[poll_id] = 0

        self.poll_id = poll_id
        self.option_id = self.generate_id(poll_id)
        self.value = value
        self.count = 0
 

    def generate_id(self, poll_id):
        '''
        generates id for option in the format 1a, 2c etc.
        '''
        id = str(poll_id) + Option.alphabets[Option.poll_id_dict[poll_id]]
        Option.poll_id_dict[poll_id] += 1
        return id

    def vote(self):
        '''
        increases the vote count by one
        '''
        self.count += 1

    def __repr__(self):
        return self.value

#comment table
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    c_option_id = db.Column(db.String(10), db.ForeignKey("option.option_id"), nullable = False)
    body = db.Column(db.Text(200), nullable = False)
    timestamp = db.Column(db.DateTime, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    anonymous = db.Column(db.Boolean, nullable = False)
    
    def __init__(self, body, option_id, user_id, anonymous = False):
        self.body = body
        self.c_option_id = option_id#comment option id
        self.user_id = user_id
        self.anonymous = anonymous
        self.timestamp = datetime.datetime.utcnow()

    def __repr__(self):
        return self.body

'''======
from app import db, login_manager
from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), index=True)
    email = db.Column(db.String(150), unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return self.email

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    #this user loader is used to restore sessions
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
>>>>>>> bedf9174c0e1298a21ee3d0cb5f1eb96eb5af694'''
