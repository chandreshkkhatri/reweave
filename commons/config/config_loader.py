import os
import configparser

config_parser = configparser.ConfigParser()
config_parser.read('./commons/config/config.ini')

if os.environ['FLASK_DEBUG'] == 'True':
    config = config_parser['DEVELOPMENT']
else:
    config = config_parser['PRODUCTION']

RESOURCES_DIR = config.get('resources_dir')