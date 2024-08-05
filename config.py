import os


class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or '123456789'
 
	basedir = os.path.abspath(os.path.dirname(__file__))
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	APP_NAME = os.environ.get('APP_NAME') or 'Dota Deck Stats'

class Static:
    API_REQUEST_DELAY = 45
    UNIX_TIME_2024 = 1722470400 # 01.08.2024
    AVG_RANK_REQUIRE = 70