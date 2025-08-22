import os
import uuid

from flask import current_app, request, redirect, url_for
from authlib.jose import jwt, JoseError
from urllib.parse import urlparse, urljoin
import PIL
from PIL import Image

from albumy.settings import Operations
from albumy.extensions import db

def generate_token(user, operation, **kwargs):
    """
    生成用于邮箱验证的Token
    :param user: 用户Id
    :param operation: 用户操作
    :param kwargs:
    :return:
    """
    # 签名算法
    header = {"alg": 'HS256', "typ": 'JWT'}
    # 加密信息密钥
    key = current_app.config['SECRET_KEY']
    # 待签名的数据负载
    data = {'id': user.id, 'operation': operation}
    data.update(**kwargs)
    token = jwt.encode(header=header, payload=data, key=key)
    # 显示设置用utf-8解码为validate_token可解码的字符串，而不是由Base64编码生成的字节串，否则在验证的时候默认使用utf-8解码字节串
    return token.decode('utf-8')

def validate_token(user, token, operation, new_password=None):
    """
    验证token令牌
    :param user:
    :param token:
    :param operation:
    :return: 根据operation操作修改数据库中的字段
    """
    key = current_app.config['SECRET_KEY']
    try:
        data = jwt.decode(token, key=key)
    except JoseError as e:
        print(f'wrong:{e}')
        return False

    if operation != data.get('operation') or user.id != data.get('id'):
        return False

    if operation == Operations.CONFIRM:
        user.confirm_statue = True

    elif operation == Operations.RESET_PASSWORD:
        user.set_hash(password=new_password)
    else:
        return False

    db.session.commit()
    return True

def redirect_up(default='main.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)

    return redirect(url_for(default, **kwargs))

def is_safe_url(target):
    host_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        test_url.netloc == host_url.netloc

def random_filename(filename):
    """生成安全的随机文件名 """
    ext = os.path.splitext(filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename

def resize_image(image, filename, base_size):
    """ 剪裁图片， 并为新剪裁的图片添加不同的后缀名 """
    img = Image.open(image)
    filename, etx = os.path.splitext(filename)
    if img.size[1] <= base_size:
        return filename + etx
    # 宽度按比例剪裁
    w_percent = (base_size/float(img.size[0]))
    # 高度按照伸缩比自动生成
    h_size = int((float(img.size[1])*float(w_percent)))
    img = img.resize((base_size, h_size))
    filename += current_app.config["ALBUMY_IMAGE_SUFFIX"][base_size] + etx
    img.save(os.path.join(current_app.config["ALBUMY_UPLOAD_PATH"], filename), optimize=True, quality=85)
    return filename