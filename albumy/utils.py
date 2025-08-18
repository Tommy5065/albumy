from flask import current_app, request, redirect, url_for
from authlib.jose import jwt, JoseError
from urllib.parse import urlparse, urljoin


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

def validate_token(user, token, operation):
    """
    验证token令牌
    :param user:
    :param token:
    :param operation:
    :return: 用户名模型类中confirm_statue变为True
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
