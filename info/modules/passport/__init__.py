from flask import Blueprint

# 登陆注册模块: 访问前缀 /passport
passport_bp = Blueprint("passport",__name__,url_prefix="/passport")

# 导入view文件中的视图函数
from .views import *