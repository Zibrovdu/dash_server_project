import configparser

cfg_parser = configparser.ConfigParser()
cfg_parser.read(r'passport/assets/settings.rkz')

token = cfg_parser['metrika']['token']

db_username = cfg_parser['connect']['username']
db_password = cfg_parser['connect']['password']
db_name = cfg_parser['connect']['db']
db_host = cfg_parser['connect']['host']
db_port = cfg_parser['connect']['port']
db_dialect = cfg_parser['connect']['dialect']
#
# schema_etsp = cfg_parser['schemas']['etsp_support']
# schema_sue = cfg_parser['schemas']['sue_support']
# schema_osp = cfg_parser['schemas']['osp_support']
# schema_employees = cfg_parser['schemas']['employees']
