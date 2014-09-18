from app import db

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(150), index = True)
	email = db.Column(db.String(150), unique = True)
	
	def __repr__(self):
		return self.email
