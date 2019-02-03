#
# class Person(object):
#
#     def __eq__(self, other):
#
#         return "查询条件 "
#
#
# if __name__ == '__main__':
#     p1 = Person()
#     print(p1)
#     p2 = Person
#     print(p2)
#     print(p1 == p2)


import functools

# 问题： 装饰器会改变被装饰的视图函数名称
# 方案：@functools.wraps(视图函数名称)


def get_user_info(view_func):
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        pass
        # 装饰功能
        # 原有函数功能
    return wrapper

@get_user_info
def index():
    pass

@get_user_info
def news_detail():
    pass


if __name__ == '__main__':
    print(index.__name__)
    print(news_detail.__name__)