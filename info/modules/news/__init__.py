from flask import Blueprint

# 登陆注册模块: 访问前缀 /passport
news_bp = Blueprint("news",__name__,url_prefix="/news")

# 导入view文件中的视图函数
from .views import *