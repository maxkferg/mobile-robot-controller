import os
from .setup import basedir



class BaseConfig():
    SECRET_KEY = "SO_SECURE"
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or "sqlite:///star.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class TestingConfig():
    """Development configuration."""
    TESTING = False
    DEBUG = False
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    DEBUG_TB_ENABLED = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
