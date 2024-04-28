class DevelopmentConfig():
    DEBUG = True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD= ''
    MYSQL_DB = 'prefeco_db'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@localhost/flaskmysql'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

config = {
    'development':DevelopmentConfig
}