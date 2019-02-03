from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
# 我们存储数据用到session
from flask import session,current_app,jsonify
import logging

from info import create_app,db
from info.models import User

"""
从单一职责的原理来思考:manage.py文件只需负责项目启动和数据库迁移即可,其他的配置信息,app相关信息都应该抽取到特定文件中.
"""
# 传入的参数是development获取开发模式对应的app对象
# 传入的参数是production获取线上模式对应的app对象
app = create_app("development")

# 6.创建管理对象
manage = Manager(app)

# 7.创建迁移对象
Migrate(app,db)

# 8.添加迁移命令
manage.add_command("db",MigrateCommand)

"""
@option("-n","--name",dest="name")
@option("-u","--url",dest="url")

命令使用:python3 manage.py createSuperuser -n "管理员账号" -p "密码"
"""


# 10.添加创建管理员用户的命令
@manage.option("-n","--username",dest="username")
@manage.option("-p","--password",dest="password")
def createSuperuser(username,password):
    """创建管理员"""

    if not all([username,password]):
        return "账号&密码不能为空"

    # 创建用户对象
    admin_user = User()
    admin_user.mobile = username
    admin_user.nick_name = username
    admin_user.password = password
    # 管理员用户
    admin_user.is_admin = True
    # 2.保存回数据库

    try:
        db.session.add(admin_user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return "保存到数据库异常"
    print("创建管理员用户成功")


if __name__ == '__main__':
    # app.run()
    # 9.使用管理对象运行项目
    manage.run()