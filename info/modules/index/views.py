from flask import current_app, render_template, session, jsonify, request, g
from info.modules.index import index_bp
from info import redis_store
# 注意：需要在别的文件中导入models中的类，让项目和models有关联
from info.models import User, News, Category
from info import constants

# 2.使用蓝图对象装饰视图函数
# 127.0.0.1:5000/ --> 项目首页
from info.response_code import RET


# 127.0.0.1：5000/news_list?cid=1&p=当前页码&per_page=每一页多少条数据
from info.utils.common import get_user_info


@index_bp.route('/news_list')
def get_news_list():
    """获取新闻列表数据后端接口"""

    """
    1.获取参数
        1.1 cid: 分类id值， p：当前页码， 默认值为：1， per_page: 每一页多少条新闻数据 默认值：10条
    2.参数校验
        2.1 非空判断
        2.2 将参数进行int强制类型转换
    3.逻辑处理
        3.1 新闻的分类id等于cid，分页查询，新闻创建的时间降序排序
        3.2 将`新闻对象`列表转换成`字典`列表
    4.返回值
        4.1 返回新闻列表数据
    """

    # 1.1 cid: 分类id值， p：当前页码， 默认值为：1， per_page: 每一页多少条新闻数据 默认值：10条
    cid = request.args.get("cid")
    p = request.args.get("p", 1)
    per_page = request.args.get("per_page", 10)

    # 2.1 非空判断
    if not cid:
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")

    # 2.2 将参数进行int强制类型转换
    try:
        cid = int(cid)
        p = int(p)
        per_page = int(per_page)
    except Exception as e:
        p = 1
        per_page = 10
        current_app.logger.error(e)

    news_list = []
    current_page = 1
    total_page = 1

    """
    if cid == 1:
    # 对于最新新闻数据，我们只需要根据时间排序即可
    paginate = News.query.filter().order_by(News.create_time.desc()) \
        .paginate(p, per_page, False)
    else:
        paginate = News.query.filter(News.category_id == cid).order_by(News.create_time.desc()) \
            .paginate(p, per_page, False)

    """

    # 查询条件列表  默认查询条件：查询审核通过的新闻
    filter_list = [News.status == 0]
    if cid != 1:
        # 除了最新分类其他都需要加上查询条件
        # sqlalchemy底层重写了__eq__方法 ==返回的是查询条件
        filter_list.append(News.category_id == cid)

    # 3.1 新闻的分类id等于cid，分页查询，新闻创建的时间降序排序
    # paginate()分页方法：参数1: 当前页码 参数2：每一页多少条数据 参数3：出错不打印
    try:
        # *列表：列表解包
        paginate = News.query.filter(*filter_list).order_by(News.create_time.desc()) \
            .paginate(p, per_page, False)

        # 提取当前页码所有数据
        news_list = paginate.items
        # 当前页码
        current_page = paginate.page
        # 总页数
        total_page = paginate.pages

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询用户对象异常")

    # 3.2 将`新闻对象`列表转换成`字典`列表
    news_dict_list = []
    for news in news_list if news_list else []:
        news_dict_list.append(news.to_dict())

    # 组织响应数据
    data = {

        "news_list": news_dict_list,
        "current_page": current_page,
        "total_page": total_page

    }
    # 4.1 返回新闻列表数据
    return jsonify(errno=RET.OK, errmsg="查询新闻列表数据成功", data=data)


@index_bp.route('/')
@get_user_info
def index():
    """展示新闻首页"""
        # -----------------------1.查询当前登录用户的信息展示-----------------------------
    user = g.user

    user_dict = user.to_dict() if user else None

    # -----------------------2.查询新闻的点击排行数据-----------------------------
    # news_rank_list = [news_obj1, news_obj2, ....]
    try:
        # 1.新闻点击量降序排序
        # 2.限制新闻条数为6条
        news_rank_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询点击排行新闻对象异常")

    # 将新闻对象列表数据转换成字典列表数据
    """
        if news_rank_list:
        for news in news_rank_list:
            news_dict = news.to_dict()
            newsrank_dict_list.append(news_dict)
    """
    newsrank_dict_list = []
    for news in news_rank_list if news_rank_list else []:
        # 将新闻对象转换成字典装入列表中
        newsrank_dict_list.append(news.to_dict())

    # -----------------------3.查询新闻的分类数据-----------------------------
    # categories = [新闻分类对象, ....]
    # 1. 查询所有的新闻分类数据
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询用户对象异常")

    # 2. 将新闻分类对象列表转换成字典列表
    category_dict_list = []
    for category in categories if categories else []:
        # 1.将对象转换成字典
        category_dict = category.to_dict()
        # 2.将字典装到列表中
        category_dict_list.append(category_dict)


    # 4.组织返回数据
    """
    数据格式：
        data = {
            "user_info" : resp_dict = {
                "id": self.id,
                "nick_name": self.nick_name,
            }
        }
    
    使用： data.user_info.nick_name
    """
    data = {
        "user_info": user_dict,
        "click_news_list": newsrank_dict_list,
        "categories": category_dict_list
    }

    return render_template("news/index.html", data=data)


# 这个视图函数是浏览器自己调用的方法，返回网站图标
@index_bp.route('/favicon.ico')
def get_faviconico():
    """返回网站的图标"""
    """
    Function used internally to send static files from the static
        folder to the browser
    内部用来发送静态文件到浏览器的方法： send_static_file
    """
    return current_app.send_static_file("news/favicon.ico")