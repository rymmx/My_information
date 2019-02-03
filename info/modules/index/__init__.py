from flask import Blueprint

# 登陆注册模块: 访问前缀 /passport
index_bp = Blueprint("index",__name__,url_prefix="/index")

# 导入view文件中的视图函数
from .views import *