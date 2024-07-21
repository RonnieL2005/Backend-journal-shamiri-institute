import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'rOnnie')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///database.db')