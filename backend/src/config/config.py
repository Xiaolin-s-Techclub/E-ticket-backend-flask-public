import os
import json
from logging import getLogger, StreamHandler, INFO, WARNING, config
import hashlib
from root_dir import ROOT_DIR
from root_config import RootConfig
from datetime import datetime
import pytz
import platform
from dotenv import load_dotenv

DAY = 1

if platform.system() == "Linux":
    # if RootConfig.DEV_MODE:
    #     DEV_MODE = True
    # else:
    DEV_MODE = False
else:
    DEV_MODE = True


# if DEV_MODE:
#     TABLE_NAME = "MIF2024_test"
# else:
#     TABLE_NAME = "MIF2024_test"
#
# USER_TABLE_NAME = "user_MIF2024_test"
TABLE_NAME = "mf24-ticket"
USER_TABLE_NAME = "mf24-user"
    # todo TABLE_NAME = "access_control"


cwd = os.getcwd()
os.chdir(ROOT_DIR)
load_dotenv("../.env")
load_dotenv("./.env")
os.chdir(cwd)
load_dotenv("./.env")

###TIMEZONE###
JST_TIMEZONE = pytz.timezone('Asia/Tokyo')

###Logging###
SRC_DIR = ROOT_DIR + "backend/src/"

with open(SRC_DIR + 'config/logging.json', 'r') as f:
    log_config = json.load(f)
    log_config["handlers"]["file"]["filename"] = \
        f'{ROOT_DIR}'+'logs/application.{}.logs'.format(datetime.now(JST_TIMEZONE).strftime("%Y%m%d%H%M"))
    config.dictConfig(log_config)

logger = getLogger(__name__)

# logger.info(ROOT_DIR)
# logger.info("env")
# logger.info("env")
# logger.info(os.environ.get("MYSQL_USER_PASSWORD"))


###DIRECTORIES###
if DEV_MODE:
    OUTPUT_TICKET_DIR = ROOT_DIR + "backend/outputs/output_ticket/"
else:
    OUTPUT_TICKET_DIR = ROOT_DIR + "backend/outputs/output_ticket/"

# mif ticket dir
# TICKET_TEMPLATE = ROOT_DIR + "backend/references/MIF2024_TICKET_TEMPLATE.png"
# music-fes ticket dir
TICKET_TEMPLATE = ROOT_DIR + "backend/references/MUSIC-FES2024_TICKET_TEMPLATE.jpg"
# TICKET_METADATA = {"qr_x": 252, "qr_y": 700, "qr_size": 600, "name_text_x": 552, "name_text_y": 1325, "font_size":51}
TICKET_METADATA = {"qr_x": 469, "qr_y": 1573, "qr_size": 1146, "name_text_x": 1042, "name_text_y": 2830, "font_size": 100}

DB_OUTPUT_DIR = ROOT_DIR + "backend/outputs/db/"

FRONT_END_STATIC_DIR = ROOT_DIR + "frontend/static"
FRONT_END_TEMPLATE_DIR = ROOT_DIR + "frontend/templates"


###Database###
class BaseConfig:
    DB_NAME = "access_control"
    # MIF2024 config
    # DB_USER = os.environ.get("MYSQL_USER")
    # DB_USER_PS = os.environ.get("MYSQL_USER_PASSWORD")

    # Music-Fes2024 config
    DB_USER = os.environ.get('DB_USER')
    DB_USER_PS = os.environ.get('DB_USER_PASSWORD')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_NAME = os.environ.get('DB_NAME', 'music_fes')
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_USER_PS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require'

    DEV_STAGE = True # DEV_MODE



class DevelopmentConfig:
    # MIF2024 config
    # SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{BaseConfig.DB_USER}:{BaseConfig.DB_USER_PS}@127.0.0.1/{BaseConfig.DB_NAME}?127.0.0.1:3306'
    # Music-Fes2024 config

    # Music-Fes2024 config
    SQLALCHEMY_DATABASE_URI = BaseConfig.SQLALCHEMY_DATABASE_URI

    # SQLALCHEMY_BINDS = {
    #     'backup': f'sqlite:///{DB_OUTPUT_DIR + datetime.now().strftime("%Y%m%d%H%M") + "_access_control"}' + '.sqlite'
    # }
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///sample_flask.db'

    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = 'Lax'

    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False

    SERVER_URL = 'http://127.0.0.1/'


class ProductionConfig:
    # MIF2024 config
    # SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{BaseConfig.DB_USER}:{BaseConfig.DB_USER_PS}@mysql/{BaseConfig.DB_NAME}?mysql:3306'

    # Music-Fes2024 config
    SQLALCHEMY_DATABASE_URI = BaseConfig.SQLALCHEMY_DATABASE_URI

    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'None'

    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False

    SERVER_URL = os.environ.get('SERVER_URL', 'https://your-domain.com/')
    # SERVER_URL = 'http://127.0.0.1/'


if DEV_MODE:
    CONFIG = DevelopmentConfig
    logger.error("Xiaolin's Development Config")
else:
    CONFIG = ProductionConfig
    logger.error("Xiaolin's Production Config")

###HASHING###
CUSTOM_HASH_STRING = os.environ.get("CUSTOM_HASH_STRING", "default-hash-string")


def convert_username_to_hash(username: str) -> str:
    hash = hashlib.new("sha256")
    # string = username + CUSTOM_HASH_STRING
    string = username + "Music-fes-2024"
    hash.update(string.encode())
    return hash.hexdigest()


###AUTHENTICATION###
WAYPOINT_API_UNAME = os.environ.get("WAYPOINT_API_UNAME")
WAYPOINT_API_PASS = os.environ.get("WAYPOINT_API_PASS")

# For MIF, it was 10
MAX_USER_TICKET_REQUEST_NUM = 2

###INFORMATION###
class_dic = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7}
grades = {"J1": 1, "J2": 2, "J3": 3, "S1": 4, "S2": 5, "S3": 6}

STUDENT_VALIDATION_INFO = {"J1":{"A":45, "B":44, "C":44, "D":44, "E":44, "F":43},
                           "J2":{"A":36, "B":37, "C":36, "D":38, "E":38, "F":34},
                           "J3":{"A":41, "B":42, "C":42, "D":42, "E":41, "F":40},
                           "S1":{"A":37, "B":39, "C":39, "D":38, "E":42, "F":50},
                           "S2":{"A":34, "B":33, "C":33, "D":35, "E":32, "F":34},
                           }

EVENT_NAME_IN_MAIL = '音楽会'

if __name__ == "__main__":
    logger.info("Configurations are loaded successfully")
    print()
