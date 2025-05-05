import os
import logging

from flask import Flask, request, session, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_babel import Babel
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# Set up logging
logging.basicConfig(level=logging.DEBUG)

csrf = CSRFProtect()

class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure the database
db_url = os.environ.get("DATABASE_URL", "sqlite:///buildingco.db")
# If using PostgreSQL, ensure we use the psycopg2 dialect
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

# Initialize the app with the CSRF extension
csrf.init_app(app)

# Configure Flask-Babel
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'bg']
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

def get_locale():
    # Check if language is set in the session
    if 'language' in session:
        return session['language']
    # Otherwise try to guess the language from the user accept
    # header the browser transmits
    return request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES'])

babel = Babel(app, locale_selector=get_locale)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

@app.before_request
def before_request():
    g.lang_code = session.get('language', request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES']) or 'en')

with app.app_context():
    # Make sure to import the models here or their tables won't be created
    import models  # noqa: F401
    
    db.create_all()
