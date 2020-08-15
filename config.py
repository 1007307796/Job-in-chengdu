import os

class Config(object):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3306/jobs?charset=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = False