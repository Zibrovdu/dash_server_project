import os
import configparser
basedir = os.path.abspath(os.path.dirname(__file__))


cfg_parser = configparser.ConfigParser()
cfg_parser.read(basedir + '\settings.rkz')

db_username = cfg_parser['connect']['username']
db_password = cfg_parser['connect']['password']
db_name = cfg_parser['connect']['db']
db_host = cfg_parser['connect']['host']
db_port = cfg_parser['connect']['port']
db_dialect = cfg_parser['connect']['dialect']


class BaseConfig:
    SQLALCHEMY_DATABASE_URI = f'{db_dialect}://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}'
    # SQLALCHEMY_DATABASE_URI = 'postgres://postgres:12345@localhost:5432/mbu_user'
    print(SQLALCHEMY_DATABASE_URI)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'my secret key'
