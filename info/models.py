from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from info import constants
from . import db


class BaseModel(object):
    """定义模型基类,为每个模型补充创建时间和更新时间"""
    create_time = db.Column(db.DateTime, default=datetime.now)  # 记录创建的时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 记录更新的时间


# 用户收藏表,建立用户与其收藏新闻多对多的关系
tb_user_collection = db.Table(
    "info_user_collection",
    db.Column("user_id", db.Integer, db.ForeignKey("info_user.id"), primary_key=True),  # 用户id
    db.Column("news_id", db.Integer, db.ForeignKey("info_news.id"), primary_key=True),  # 新闻id
    db.Column("create_time",db.DateTime,default=datetime.now)  # 创建收藏时间
)

# 粉丝关系表,自关联多对多
tb_user_follows = db.Table(
    "info_user_fans",
    db.Column("follower_id", db.Integer,db.ForeignKey("info_user.id"), primary_key=True),  # 粉丝id
    db.Column("followed_id", db.Integer,db.ForeignKey("info_user.id"), primary_key=True),  # 被关注人id
)


class User(BaseModel,db.Model):
    """用户"""
    __tablename__ = "info_user"

    id = db.Column(db.Integer, primary_key=True)  # 用户id
    nick_name = db.Column(db.String(32), unique=True, nullable=False)  # 用户昵称
    password_hash = db.Column(db.String(128), nullable=False)  # hash加密的密码
    mobile = db.Column(db.String(11), unique=True, nullable=False)  # 手机号
    avatar_url = db.Column(db.String(256))  # 用户头像路径
    last_login = db.Column(db.DateTime, default=datetime.now)  # 最后一次登陆时间
    is_admin = db.Column(db.Boolean, default=False)  # 是否管理员
    signature = db.Column(db.String(512))  # 用户签名
    gender = db.Column(db.Enum("MAN", "WOMAN"), default="MAN")  #性别

    # user.collection_news : 查询当前用户收藏的新闻列表对象数据
    # lazy="dynamic"  : 真正使用数据的时候: 新闻列表   如果只是简单查询:查询对象
    collection_news = db.relationship("News", secondary=tb_user_collection, lazy="dynamic")  # 用户收藏的新闻

    # 用户所有的粉丝,添加了反向引用followed,代表用户都关注了那些人
    # user.followers 查询当前用户的粉丝列表数据
    # user.followed 查询当前用户的关注列表数据
    followers = db.relationship("User",
                                secondary=tb_user_follows,
                                primaryjoin=id == tb_user_follows.c.followed_id,
                                secondaryjoin=id == tb_user_follows.c.followed_id,
                                backref=db.backref("followed", lazy="dynamic"),
                                lazy="dynamic")

    # user.news_list :查询当前用户发布的新闻列表
    # news.user :查询当前新闻发布的作者
    news_list = db.relationship("News", backref="user", lazy="dynamic")  #当前用户所发布的新闻

    def set_password_hash(self, password):
        """
        密码加密
        :param password: 未加密的密码
        :return:
        """
        # 获取加密后的密码
        password_hash = generate_password_hash(password)
        # 给当前对象的password_hash 赋值
        self.password_hash = password_hash

    # get方法,获取值的时候触发
    @property
    def password(self):
        raise AttributeError("密码不允许被获取")

    # set方法,给属性赋值的时候触发
    @password.setter
    def password(self, value):
        """
        密码加密
        :param value: 未加密的密码
        :return:
        """
        # 获取加密后的密码
        password_hash = generate_password_hash(value)
        # 给当前对象的password_hash 赋值
        self.password_hash = password_hash

    # 检查用户填写的密码和数据库保存的密码是否一致
    def check_password(self, password):
        """
        密码校验
        :param password: 未加密密码
        :return: Bool
        """
        # 如果密码一致返回True,反之返回False
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """
        将对象转化为字典
        隐藏数据库的字段[更安全]
        :return:
        """
        resp_dict = {
            "id": self.id,
            "nick_name": self.nick_name,
            "avater_url": constants.QINIU_DOMIN_PREFIX + self.avatar_url if self.avatar_url else "",
            "mobile": self.mobile,
            "gender": self.gender if self.gender else "MAN",
            "signature": self.signature if self.signature else "",
            "followers_count": self.followers.count(),
            "news_count": self.news_list.count()
        }

        return resp_dict

    def to_admin_dict(self):
        resp_dict = {
            "id": self.id,
            "nick_name": self.nick_name,
            "mobile": self.mobile,
            "register": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": self.last_login.strftime("%Y-%m-%d %H:%M:%S")
        }

        return resp_dict


class News(BaseModel, db.Model):
    """新闻"""
    __tablename__ = "info_news"

    id = db.Column(db.Integer, primary_key=True)  # 新闻id
    title = db.Column(db.String(256), nullable=False)  # 新闻标题
    source = db.Column(db.String(64), nullable=False)  # 新闻来源
    digest = db.Column(db.String(512), nullable=False)  # 新闻摘要

    content = db.Column(db.Text, nullable=False)  # 新闻内容

    clicks = db.Column(db.Integer, default=0)  # 浏览量
    index_image_url = db.Column(db.String(256))  # 新闻列表图片路径
    category_id = db.Column(db.Integer, db.ForeignKey("info_category.id"))  # 新闻种类id
    user_id = db.Column(db.Integer, db.ForeignKey("info_user.id"))  # 新闻的作者id
    status = db.Column(db.Integer, default=0)  # 当前新闻状态: 0审核通过 1审核中 -1审核未通过
    reason = db.Column(db.String(256))  # 未通过的原因,status=-1 的时候使用

    # news.comments :查询当前新闻评论数据
    comments = db.relationship("Comment", lazy="dynamic")  # 当前新闻的所有评论

    def to_review_dict(self):
        resp_dict = {
            "id": self.id,
            "title": self.title,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": self.status,
            "reason": self.reason if self.reason else ""
        }
        return resp_dict

    def to_basic_dict(self):
        resp_dict = {
            "id": self.id,
            "title": self.title,
            "source": self.source,
            "digest": self.digest,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "index_image_url": self.index_image_url,
            "clicks": self.clicks
        }
        return resp_dict

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "title": self.title,
            "source": self.source,
            "digest": self.digest,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "content": self.content,
            "comments_count": self.comments.count(),
            "clicks": self.clicks,
            "category": self.category.to_dict(),
            "index_image_url": self.index_image_url,
            "author": self.user.to_dict() if self.user else None
        }


class Comment(BaseModel, db.Model):
    """评论"""
    __tablename__ = "info_comment"

    id = db.Column(db.Integer,primary_key=True)  # 评论id
    user_id = db.Column(db.Integer, db.ForeignKey("info_user.id"), nullable=False)  # 用户id
    news_id = db.Column(db.Integer, db.ForeignKey("info_news.id"), nullable=False)  # 新闻id

    content = db.Column(db.Text, nullable=False)  # 评论内容

    parent_id = db.Column(db.Integer, db.ForeignKey("info_comment.id"), nullable=False)  # 父评论id
    # 子评论.parent :查询当前子评论对应的父评论
    parent = db.relationship("Comment", remote_side=[id])  # 自关联
    like_count = db.Column(db.Integer, default=0)  # 点赞条数

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "content": self.content,
            "parent": self.parent.to_dict() if self.parent else None,
            "user": User.query.get(self.user_id).to_dict(),
            "news_id": self.news_id,
            "like_count": self.like_count
        }
        return resp_dict


class CommentLike(BaseModel, db.Model):
    """评论点赞"""
    __tablename__ = "info_comment_like"

    comment_id = db.Column("comment_id", db.Integer, db.ForeignKey("info_comment.id"), primary_key=True)  # 评论id
    user_id = db.Column("user_id", db.Integer, db.ForeignKey("info_user.id"), primary_key=True)  #用户id


class Category(BaseModel, db.Model):
    """新闻分类"""

    __tablename__ = "info_category"

    id = db.Column(db.Integer, primary_key=True)  # 分类id
    name = db.Column(db.String(64), nullable=False)  # 分类名

    # category.news_list : 查询当前分类对应的新闻列表
    # news.category : 查询当前新闻属于哪个新闻

    # 一对多关系
    news_list = db.relationship("News", backref="category", lazy="dynamic")

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "name": self.name
        }

        return resp_dict

