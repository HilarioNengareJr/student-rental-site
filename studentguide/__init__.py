from flask import Flask
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap
from flask_dropzone import Dropzone
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
dropzone = Dropzone(app)

app.config['SECRET_KEY'] = 'Sick Rat'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.png', '.jpg', '.jpeg', '.gif']
app.config['DROPZONE_UPLOAD_MULTIPLE'] = True
app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_INPUT_NAME'] = 'file'
app.config['DROPZONE_MAX_FILES'] = 5 * 1024
app.config['DROPZONE_TIMEOUT'] = 45
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image/*'
app.config['UPLOAD_PATH'] = './studentguide/static/uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///studentguide.db'
bootstrap = Bootstrap(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = '___@gmail.com'  # come back to email reset password
app.config['MAIL_PASSWORD'] = ''
mail = Mail(app)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

def make_list(_var):
    return eval(_var)


app.jinja_env.globals.update(make_list=make_list)

from studentguide import routes
