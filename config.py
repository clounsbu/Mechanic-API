class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:Greyghost514@localhost/mechanic_db'
    DEBUG = True
    CACHE_TYPE =  'SimpleCache'
    CACHE_TIMEOUT_DEFAULT = 300


    class TestingConfig:
        pass

    class ProductionConfig: 
        pass