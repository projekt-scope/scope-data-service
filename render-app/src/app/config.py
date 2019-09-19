""" Global Flask Application Settings """

import os
from app import app


class Config(object):
    DEBUG = False
    TESTING = False
    PRODUCTION = False


class Development(Config):
    MODE = "Development"
    DEBUG = True

    ACAO = "*"  # Access-Control-Allow-Origin

    SECRET = "SuperSecretRandomString"
    SECRET_KEY = SECRET
    SECURITY_PASSWORD_SALT = SECRET
    FLASK_SECRET = SECRET

    SQLALCHEMY_DATABASE_URI = "sqlite:///db_test.sqlite3/"


# Set FLASK_CONFIG env to 'Production' or 'Development' to set Config
flask_config = os.environ.get("FLASK_CONFIG", "Development")
app.config.from_object("app.config.{}".format(flask_config))
