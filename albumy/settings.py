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
    MAIL_DEFAULT_SENDER = ('Albumy', os.getenv('MAIL_USERNAME'))

    DROPZONE_MAX_FILE_SIZE = 3  # 在客户端对文件传输大小过滤 最大3MB
    DROPZONE_MAX_FILES = 30  # 在客户端一次上传的最大文件数量
    DROPZONE_ALLOWED_FILE_TYPE = 'image'  # 接收flask-dropzone内置的文件类型为图片
    DROPZONE_ENABLE_CSRF = True  # 在文件上传区域表单添加隐藏csrf令牌验证字段
    MAX_CONTENT_LENGTH = 3*1024*1024  # 在服务器端对文件传输大小过滤
    ALBUMY_UPLOAD_PATH = os.path.join(basedir, 'upload')
    ALBUMY_IMAGE_SIZE = {'small': 400, 'medium': 800}
    ALBUMY_IMAGE_SUFFIX = {
        ALBUMY_IMAGE_SIZE['small']: '_s',
        ALBUMY_IMAGE_SIZE['medium']: '_m'
    }


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')

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