from app import db
import string
import datetime

#user table
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(150), index = True, nullable = False)
    email = db.Column(db.String(150), unique = True, nullable = False)
    password_hash = db.Column(db.String(128), nullable = False)#hashed_password
    polls = db.relationship("Poll", lazy = "dynamic")
	
    def __repr__(self):
        return self.email

#poll table
class Poll(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.Text(1000), nullable = False)
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    cat_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable = False)
    options = db.relationship("Option", lazy = "dynamic")
    def __init__(self, id, body, user_id, cat_id, timestamp):
        if timestamp is None:
            timestamp = datetime.datetime.utcnow()
        self.id = id
        self.body = body
        self.user_id = user_id
        self.cat_id = cat_id
        self.timestamp = datetime.datetime.utcnow()

    def __repr__(self):
        return self.body

#category table
class Category(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(150), unique = True, index = True, nullable = False)
    polls = db.relationship("Poll", lazy = "dynamic")

    def __repr__(self):
        return self.name

#option table
class Option(db.Model):
    alphabets = string.ascii_lowercase
    poll_id_dict = {}
    poll_id = db.Column(db.Integer, db.ForeignKey("poll.id"), nullable = False)
    id = db.Column(db.String(10), primary_key = True)
    value = db.Column(db.String(100), index = True, nullable = False)
    count = db.Column(db.Integer, nullable = False)
    comments = db.relationship("Comment")

    
    def __init__(self, poll_id, id, value):
        if poll_id not in poll_id_dict.keys():
            poll_id_dict[poll_id] = 0

        self.poll_id = poll_id
        self.id = self.generate_id(poll_id)
        self.value = value
        self.count = 0
 

    def generate_id(self, poll_id):
        '''
        generates id for option in the format 1a, 2c etc.
        '''
        id = str(poll_id) + alphabets[poll_id_dict[poll_id]]
        poll_id_dict[poll_id] += 1
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
    id = db.Column(db.String(10), db.ForeignKey("option.id"), primary_key = True)
    body = db.Column(db.Text(2000), nullable = False)
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return self.body
