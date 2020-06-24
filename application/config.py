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

    # local postgresql

    # Postgresに切り替え(Heroku運用時は以下を使用)
    SQLALCHEMY_DATABASE_URI = 'postgres://mowqryumiquugc:1f10d9a4c095458db1671e03a1330207d3ad4f65a531e5d34182d22239785f83@ec2-50-17-90-177.compute-1.amazonaws.com:5432/d730lg12eavam0'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True


Config = DevelopmentConfig
