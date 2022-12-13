import os
import configparser

config_parser = configparser.ConfigParser()
config_parser.read('./commons/config/config.ini')

config = config_parser['DEVELOPMENT']

RESOURCES_DIR = config.get('resources_dir')