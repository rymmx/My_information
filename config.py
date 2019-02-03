import logging
from redis import StrictRedis


# 0.创建项目配置类
class Config(object):
    """自定义项目配置父类"""

    # mysql数据库配置
    # 连接配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:123456@localhost:3306/information23"

    # 开启数据库跟踪修改操作
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 当数据库回话对象关闭的时候,开启自动提交数据的功能  等同于db.session.commit()
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    # redis 数据库配置信息
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = "6379"

    # 设置session需要设置加密字符串
    SECRET_KEY = "lkfj JKHIkjnnjkdfj2343"

    # 将flask.session的存储从 服务器内存调整到redis数据库 配置如下
    SESSION_TYPE = "redis"  # 标明存储的数据库类型
    SESSION_REDIS = StrictRedis(host=REDIS_HOST,port=REDIS_PORT,db=1)  # redis对象
    SESSION_USER_SIGNER = True  # 对于session_id需要进行加密处理
    SESSION_PERMANENT = False  # redis中的数据不需要永久存储
    PERMANENT_SESSION_LIFETIME = 86400  # 设置redis中session过期时常


class DevelopmentConfig(Config):
    """开发模式的项目配置信息"""

    #开启项目调试模式
    DEBUG = True

    # 开发模式的日志等级设置为:DEBUG
    LOG_LEVEL = logging.DEBUG


class ProductionConfig(Config):
    """线上模式的项目配置信息"""

    # 线上模式不需要debug信息减少io压力
    DEBUG = False

    # 线上模式的日志等级设置为:ERROR
    LOG_LEVEL = logging.ERROR


# 提供一个接口供外界使用
# 使用方式 config_dict["development"]  --> DevelopmentConfig
config_dict = {
    "development":DevelopmentConfig,
    "production":ProductionConfig
}