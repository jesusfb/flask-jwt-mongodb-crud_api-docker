import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv() 

class Config(object):
    DEBUG = False
    TESTING = False
    JWT_SECRET_KEY = 'Library_jwtPrivateKey'
    MONGO_URI = f"mongodb+srv://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_CLUSTER')}/{os.getenv('DB_DATABASE')}"
    # Set expiration time to 30 minutes
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True

app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
