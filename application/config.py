import os
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


class DevelopmentConfig:
    # Flask
    DEBUG = True
    SECRET_KEY = os.urandom(24)

    # sqlite3
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # Postgresに切り替え(Heroku運用時は以下を使用)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'postgres://localhost/bookmanager'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True


Config = DevelopmentConfig
