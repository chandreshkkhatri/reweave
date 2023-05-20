import os
import configparser
from pydantic import BaseSettings

from microservices.commons.enums.environment import Environment

config_parser = configparser.ConfigParser()
config_parser.read('./commons/config/config.ini')
env_config = config_parser['SETTINGS']

class Settings(BaseSettings):
    env_name: str = env_config['ENV_NAME']
    db_name: str = env_config['DB_NAME']
    db_host: str = env_config['DB_HOST']
    RESOURCES_DIR: str = env_config['RESOURCES_DIR']
    local_fe_host: str = env_config['LOCAL_FE_HOST']
    production_fe_host: str = env_config['PRODUCTION_FE_HOST']