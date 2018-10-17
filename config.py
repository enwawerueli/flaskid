import os


class Config(object):

    SECRET_KEY = os.environ.get('SKY_KEY') or 'some random string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')

    @staticmethod
    def configure(app):
        """ override to provide configuration specific initialization """
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database-devel.sqlite3'
    BOOTSTRAP_SERVE_LOCAL = True

    @staticmethod
    def configure(app):
        pass


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database-test.sqlite3'

    @staticmethod
    def configure(app):
        pass


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.sqlite3'

    @staticmethod
    def configure(app):
        pass


config = dict(
    development=DevelopmentConfig,
    testing=TestingConfig,
    production=ProductionConfig,
    default=DevelopmentConfig
)
