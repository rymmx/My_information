import qiniu
from flask import current_app

# 和七牛云对接的秘钥
access_key = "W0oGRaBkAhrcppAbz6Nc8-q5EcXfL5vLRashY4SI"
secret_key = "tsYCBckepW4CqW0uHb9RdfDMXRDOTEpYecJAMItL"

# 空间名字
bucket_name = "information23"


def pic_store(data):
    """
    上传图片数据到七牛云
    data: 图片二进制数据
    """

    if not data:
        raise AttributeError("图片数据为空")

    try:
        # 用户权限校验
        q = qiniu.Auth(access_key, secret_key)
        # 图片名称 一般不自己指明，七牛云会自动分配一个唯一的图片名字
        # key = 'hello'

        token = q.upload_token(bucket_name)
        # 上传图片二进制数据到七牛云
        ret, info = qiniu.put_data(token, None, data)
    except Exception as e:
        current_app.logger.error(e)
        raise AttributeError("上传图片到七牛云异常")

    print(ret)
    print("-----------")
    print(info)

    if ret is not None:
        print('All is OK')
    else:
        print(info)  # error message in info

    if info.status_code != 200:
        # 上传图片失败
        raise AttributeError("上传图片到七牛云异常")

    # 图片名称
    return ret["key"]


if __name__ == '__main__':
    file_name = input("输入图片路径:")
    with open(file_name, "rb") as f:
        data = f.read()
        pic_store(data)