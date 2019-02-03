from flask import Blueprint

# 登陆注册模块: 访问前缀 /passport
admin_bp = Blueprint("admin",__name__,url_prefix="/admin")

# 导入view文件中的视图函数
from .views import *