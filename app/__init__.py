from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.wtf.csrf import CsrfProtect
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.mail import Mail
from momentjs import momentjs


app = Flask(__name__)
#pick configurations from config.py
app.config.from_object('config')

#initialise flask-login manager
login_manager = LoginManager(app)

#initialise database
db = SQLAlchemy(app)

#initialize mail
mail = Mail(app)

app.jinja_env.globals['momentjs'] = momentjs


from app import views, models

#define the view to be redirected to in case of unauthenticated user
login_manager.login_view = 'login'
