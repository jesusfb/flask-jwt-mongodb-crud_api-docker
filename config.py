import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv() 

class Config(object):
    DEBUG = False
    TESTING = False
    JWT_SECRET_KEY = 'Library_jwtPrivateKey'
    MONGO_URI = f"mongodb+srv://jesusfb:Dove3229-@cluster0.yx9sjqo.mongodb.net/crudflask"
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
