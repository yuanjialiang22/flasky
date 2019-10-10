import os
from globalvarconfig import getGlobalVars

basedir = os.path.abspath(os.path.dirname(__file__))
# globalVars = getGlobalVars()
# HOST, USER, PASSWORD, DB, CHARSET = globalVars.mysqlData()
# MAIL_SERVER, MAIL_PORT, MAIL_ADDRESS, MAIL_PWD, ADMIN_EMAIL = globalVars.emailData()
# MP_USER, MP_PASSWORD, MP_HOST, MP_DB = globalVars.manPowerData()


class Config:
    # SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    # MAIL_SERVER = os.environ.get('MAIL_SERVER', MAIL_SERVER)
    # MAIL_PORT = int(os.environ.get('MAIL_PORT', MAIL_PORT))
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME', MAIL_ADDRESS)
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', MAIL_PWD)
    # FLASKY_MAIL_SUBJECT_PREFIX = '[ AMMIC ]'
    # FLASKY_MAIL_SENDER = MAIL_ADDRESS
    # FLASKY_ADMIN = ADMIN_EMAIL
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    # SQLALCHEMY_TRACH_MODIFICATIONS = False
    FLASKY_POSTS_PER_PAGE = 20
    FLASKY_POSTS_PER_MCLPAGE = 12

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    MAIL_SERVER = 'smtp.263.net'
    MAIL_PORT = 587
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = 'yuanjialiang@ammic.com.cn'
    MAIL_PASSWORD = 'yuan2333'
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'yuanjialiang@ammic.com.cn'
    FLASKY_ADMIN = 'yuanjialiang@ammic.com.cn'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://yuanjl:111111@localhost:3306/python?charset=utf8'
    # SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{USER}:{PASSWORD}@{HOST}:3306/{DB}?charset={CHARSET}'
    # SQLALCHEMY_BINDS = {
    #     'ManPower': f'oracle://{MP_USER}:{MP_PASSWORD}@{MP_HOST}:1521/{MP_DB}'
    # }

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://yuanjl:111111@localhost:3306/python?charset=utf8'
    #SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{USER}:{PASSWORD}@{HOST}:3306/{DB}?charset={CHARSET}'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://yuanjl:111111@localhost:3306/python?charset=utf8'
    #SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{USER}:{PASSWORD}@{HOST}:3306/{DB}?charset={CHARSET}'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}