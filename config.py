import os
from sqlalchemy import create_engine
basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    SQLALCHEMY_DATABASE_URI = 'postgres://mbu_user:qwer@localhost:5432/mbu_user'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'my secret key'
    engine = create_engine('postgres://mbu_user:qwer@localhost:5432/mbu_user')
