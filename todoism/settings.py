import os
import sys

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

if sys.platform.startswith('win'):
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


class BaseConfig:
    TODOISM_ITEM_PER_PAGE = 20
    TODOISM_LOCALES = ['en_US', 'zh_Hans_CN']

    # SERVER_NAME = 'miali.dev:5000'
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret string')

    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'data.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BABEL_DEFAULT_LOCALE = TODOISM_LOCALES[1]

    APISPEC_SPEC = APISpec(
        title='pets',
        version='1.0.0',
        openapi_version='3.0.2',
        plugins=[MarshmallowPlugin()],
    )
    APISPEC_SWAGGER_URL = '/swagger/'


class DevelopmentConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

