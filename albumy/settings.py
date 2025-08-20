import os

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret string')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_USE_SSL = True
    MAIL_PORT = 465
    MAIL_DEFAULT_SENDER = ('Albumy',os.getenv('MAIL_USERNAME'))

class DevelopmentConfig(BaseConfig):
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.db')
    SQLALCHEMY_DATABASE_URI = 'mysql://ToMan:root123@localhost/albumy'

class TestingConfig(BaseConfig):
    TestingConfig = True
    WTF_CSRF_ENABLE = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite' + os.path.join(basedir,'data.db'))

class Operations:
    CONFIRM = 'confirm'
    RESET_PASSWORD = 'reset_password'
    CHANGE_EMAIL = 'change_email'

Config = {
    "development" : DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig
}