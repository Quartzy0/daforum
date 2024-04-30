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
DATABASE_UUID_SUPPORT = environ.get('DATABASE_UUID_SUPPORT') == "1" or "sqlite" not in SQLALCHEMY_DATABASE_URI

# Upload Settings
MINIO_URL = environ.get('MINIO_URL') or "127.0.0.1:9000"
MINIO_ACCESS_KEY = environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = environ.get('MINIO_SECRET_KEY')
MINIO_SECURE_CONNECTION = environ.get('MINIO_SECURE_CONNECTION') or False
MINIO_BUCKET = environ.get('MINIO_BUCKET')
MINIO_ENDPOINT = environ.get('MINIO_ENDPOINT') or 'http://127.0.0.1:9000/' + MINIO_BUCKET + "/"
