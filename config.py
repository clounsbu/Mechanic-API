import os

class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:Greyghost514@localhost/mechanic_db'
    DEBUG = True
    CACHE_TYPE =  'SimpleCache'
    CACHE_TIMEOUT_DEFAULT = 300


class TestingConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'
    DEBUG = True
    CACHE_TYPE = 'SimpleCache'
    TESTING = True


class ProductionConfig: 
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    CACHE_TYPE = 'SimpleCache'

    