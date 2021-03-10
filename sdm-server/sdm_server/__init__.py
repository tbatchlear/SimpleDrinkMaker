# This file performs initial package setup
# and application variable configuration.
from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, logging

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "http://localhost:3000"}})
logging.getLogger('flask_cors').level = logging.DEBUG
app.config['TESTING'] = False
app.config['SECRET_KEY'] = 'Not_A_Good_Key_Replace_When_Deploy_To_Production'
# SQLite is used in development. When pushed to production, the SQLALCHEMY_DATABASE_URI must be
# replaced with the MySQL host, username, and password
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sdm-server.db'
app.config['MAIL_SERVER'] = 'email-smtp.us-east-1.amazonaws.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = ''#removed from commit
app.config['MAIL_PASSWORD'] = ''#removed from commit
mail = Mail(app)
db = SQLAlchemy(app)

from sdm_server import routes

