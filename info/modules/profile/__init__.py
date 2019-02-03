from flask import Blueprint

# 登陆注册模块: 访问前缀 /passport
profile_bp = Blueprint("passport",__name__,url_prefix="/user")

# 导入view文件中的视图函数
from .views import *