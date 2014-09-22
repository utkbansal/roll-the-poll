from flask import Flask
#from app import views
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

app = Flask(__name__)
#pick configurations from config.py
app.config.from_object('config')

#initialise flask-login manager
login_manager = LoginManager(app)

#initialise database
db = SQLAlchemy(app)


from app import views, models

#define the view to be redirected to in case of unauthenticated user
login_manager.login_view = 'login'