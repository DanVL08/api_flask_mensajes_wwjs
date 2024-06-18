class DevelopmentConfig:
    DEBUG = True
    MYSQL_HOST = 'https://mysql-prefeapp.alwaysdata.net'
    MYSQL_USER = 'prefeapp_1'
    MYSQL_PASSWORD = 'U8_k5ETiK2T_Myi'
    MYSQL_DB = 'prefeapp_db'
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

config = {
    'development':DevelopmentConfig
}