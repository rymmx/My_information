import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, g, render_template

# session 拓展工具,将flask中的session存储调整到redis
from flask_session import Session

from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from redis import StrictRedis

from config import config_dict
from info.utils.common import get_user_info, do_ranklist_class

# 当app不存在时,只是进行声明,没有真正创建数据库对象db
db = SQLAlchemy()

# 全局变量,声明未空类型数据
redis_store = None  # type:StrictRedis


def write_log(config_class):

    # 设置日志的记录等级
    # DevelopmentConfig.LOG_LEVEL == logging.DEBUG
    # ProductionConfig.LOG_LEVEL == logging.ERROR
    logging.basicConfig(level=config_class.LOG_LEVEL)  # 调试debug级

    # 创建日志记录器,指明日志保存的路径,每个日志文件的最大大小,保存日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)

    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')

    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)

    # 为全局的日志工具对象(flask app 使用的) 添加日志记录器
    logging.getLogger().addHandler(file_log_handler)



# 工厂方法
# development --> DevelopmentConfig
# production -->  ProductionConfig
def create_app(config_name):
    # 1.创建app对象
    app = Flask(__name__)

    # 2.将配置信息添加到app上
    config_class = config_dict[config_name]  # DevelopmentConfig

    # 记录日志
    write_log(config_class)

    # DevelopmentConfig   --->赋予app属性为开发模式app
    #ProductionConfig---> 赋予app属性为:线上模式app
    app.config.from_object(config_class)

    # 3.数据对象(mysql和redis)
    # mysql 数据库对象
    # 延迟加载,懒加载,当app有值时才真正进行数据库初始化工作
    db.init_app(app)

    # redis 数据库对象
    global redis_store
    redis_store = StrictRedis(host=config_class.REDIS_HOST,port=config_class.REDIS_PORT,decode_responses=True)

    # 4.给项目添加csrf保护机制
    # 1.提取cookie中的csrf_tocken
    # 2.如果数据是通过表单发送:提取表单中csrf_token,如果数据是通过ajax请求发送的;提取请求头中的字段X-CSRFToken
    # 3.对比两个值是否一致
    CSRFProtect(app)

    # 利用钩子函数在每次请求之后设置csrf_token 值到cookie中
    @app.after_request
    def set_csrf_token(response):
        """补充csrf_token的逻辑"""

        # 1.生成csrf_token随机值
        csrf_token = generate_csrf()
        # 2.获取相应对象,统一设置csrf_token值到cookie中
        response.set_cookie("csrf_token",csrf_token)
        # 3.返回响应对象
        return response

    # 通过app对象将函数添加到系统过滤器中
    app.add_template_filter(do_ranklist_class,"ranklist_class")

    # 捕获404异常,返回404统一页面
    # 注意: 需要接受err信息
    @app.errorhandler(404)
    @get_user_info
    def handler_404notfound(err):

        # 1.查询用户信息
        user = g.user
        data = {
            "user_info":user.to_dict() if user else None
        }

        # 2.返回404页面
        return render_template("news/404.html",data=data)


    # 5.创建Flask_session工具类对象:将flask.session的存储从 服务器内存 调整到redis 数据库
    Session(app)

    # 注意:真正使用蓝图对象时才导入,能够解决循环导入问题
    # 在app 上注册蓝图
    # 注册首页蓝图对象
    # from info.modules.index import index_bp
    # app.register_blueprint(index_bp)

    # 添加注册模块蓝图
    # from info.modules.passport import passport_bp
    # app.register_blueprint(passport_bp)

    # 注册新闻的蓝图对象
    # from info.modules.news import news_bp
    # app.register_blueprint(news_bp)

    return app





