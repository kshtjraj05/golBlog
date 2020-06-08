import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
    SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DATABASE_URI')
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT= 587
    POSTS_PER_PAGE=10
    MAIL_USE_TLS=True
    MAIL_USERNAME=os.environ.get('EMAIL_USERNAME')
    MAIL_PASSWORD=os.environ.get('EMAIL_PASS')