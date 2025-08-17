from flask import current_app, request, redirect, url_for
from itsdangerous import TimedSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from urllib.parse import urlparse, urljoin

from albumy.settings import Operations
from albumy.extensions import db

def generate_token(user, operation, expire_in=None, **kwargs):
    """
    生成token令牌
    :param user:
    :param operation: 生成的token的目的，本次是验证用户邮箱
    :param expire_in: 过期时间，默认1小时
    :param kwargs: 关键字参数
    :return: 最终生成的签名
    """
    s = Serializer(current_app.config['SECRET_KEY'], expire_in)
    data = {'id': user.id, 'operation': operation}
    data.update(**kwargs)
    return s.dumps(data)


def validate_token(user, token, operation):
    """
    验证token令牌
    :param user:
    :param token:
    :param operation:
    :return: 用户名模型类中confirm_statue变为True
    """
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except (BadSignature, SignatureExpired):
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
