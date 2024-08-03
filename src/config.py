import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


load_dotenv()


PROD = True

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR.parent / "static"
TEMPLATES_DIR = BASE_DIR.parent / "templates"


DB_HOST: str
DB_PORT: str
DB_NAME: str
DB_USER: str
DB_PASS: str

REDIS_HOST: str
REDIS_PORT: int


if PROD:
    DB_HOST = os.environ.get("DB_HOST")
    DB_PORT = os.environ.get("DB_PORT")
    DB_NAME = os.environ.get("DB_NAME")
    DB_USER = os.environ.get("DB_USER")
    DB_PASS = os.environ.get("DB_PASS")

    REDIS_HOST = os.environ.get("REDIS_HOST")
    REDIS_PORT = os.environ.get("REDIS_PORT")
else:
    DB_HOST = "localhost"
    DB_PORT = "5432"
    # DB_NAME = "postgres"
    # DB_USER = "postgres"
    # DB_PASS = "postgres"
    DB_NAME = "athkeeper"
    DB_USER = "athuser"
    DB_PASS = "ATHkeeper2023"

    REDIS_HOST = "localhost"
    REDIS_PORT = 6379


DB_HOST_TEST = os.environ.get("DB_HOST_TEST")
DB_PORT_TEST = os.environ.get("DB_PORT_TEST")
DB_NAME_TEST = os.environ.get("DB_NAME_TEST")
DB_PASS_TEST = os.environ.get("DB_PASS_TEST")
DB_USER_TEST = os.environ.get("DB_USER_TEST")


SEKRET_KEY = os.getenv('SEKRET_KEY')
ALGORITHM = 'HS256'


ORIGINS = [
    "https://athkeeper.com",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
]

ALLOW_METHODS = ['*']
ALLOW_HEADERS = ['*']
