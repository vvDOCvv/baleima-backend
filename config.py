import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


BASE_DIR = Path(__file__).parent


load_dotenv()


class Settings(BaseSettings):
    db_url: str = f'sqlite+aiosqlite:///{BASE_DIR}/db.sqlite'
    db_echo: bool = True


DB_NAME = os.getenv('DB_LOGIN')
DB_LOGIN = os.getenv('DB_LOGIN')
DB_PASSWORD = os.getenv('DB_LOGIN')

SEKRET_KEY = os.getenv('SEKRET_KEY')
ALGORITHM = 'HS256'


DB_POSTGRESS_URL = f"postgesql+asyncpg://{DB_LOGIN}:{DB_PASSWORD}@localhost/{DB_NAME}"


settings = Settings()


