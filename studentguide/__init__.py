import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

app = Flask(__name__)

app.config['SECRET_KEY'] = 'Sick Rat'

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.png', '.jpg', '.jpeg', '.gif']
app.config['UPLOAD_PATH'] = './studentguide/static/uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///studentguide.db'
bootstrap = Bootstrap(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

from studentguide import routes
