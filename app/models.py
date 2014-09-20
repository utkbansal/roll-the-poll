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

    '''@property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)'''

    #this user loader is used to restore sessions
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))