import configparser

cfg_parser = configparser.ConfigParser()
cfg_parser.read(r'assets/settings.rkz')

token = cfg_parser['metrika']['token']

db_username = cfg_parser['connect']['username']
db_password = cfg_parser['connect']['password']
db_name = cfg_parser['connect']['db']
db_host = cfg_parser['connect']['host']
db_port = cfg_parser['connect']['port']
db_dialect = cfg_parser['connect']['dialect']

etsp_table_name = cfg_parser['table_names']['etsp_table']
sue_table_name = cfg_parser['table_names']['sue_table']
osp_table_name = cfg_parser['table_names']['osp_table']

con_mail_server = [cfg_parser['mail']['server'], cfg_parser['mail']['user'], cfg_parser['mail']['password']]


new_task_subject = 'На Вас назначена задача / проект'
exist_task_subject = 'Внесены изменения по задаче / проекту'
