from os import environ, path

# The folder where our web application
# with the subfolders resides / "lives"
BASE_DIR = path.abspath(path.dirname(__file__))

# General Flask Settings
SECRET_KEY = environ.get('SECRET_KEY') or 'some long and not easily gueassable strings'
#FLASK_APP = app.py
FLASK_DEBUG = 1 # 1 for development, 0 for production

# Database Settings
DATABASE_FILE = 'sqlite:///' + path.join(BASE_DIR, 'db.sqlite')
SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL') or DATABASE_FILE
SQLALCHEMY_TRACK_MODIFICATION = False

# Upload Settings
UPLOAD_DIR = path.join(BASE_DIR, 'static/upload')
