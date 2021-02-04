import os
basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    SQLALCHEMY_DATABASE_URI = 'postgres://postgres:12345@localhost:5432/mbu_user'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'my secret key'
