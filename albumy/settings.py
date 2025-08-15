import os

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
class BaseConfig:
    SECRETE_KEY = os.getenv('SECRET-KEY', 'secret string')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.db')

class TestingConfig(BaseConfig):
    TestingConfig = True
    WTF_CSRF_ENABLE = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite' + os.path.join(basedir,'data.db'))

Config = {
    "development" : DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig
}