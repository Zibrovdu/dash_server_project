import os
basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    SQLALCHEMY_DATABASE_URI = f'postgres://postgres:6002815@192.168.1.4:5432/test'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'my secret key'
