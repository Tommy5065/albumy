from flask import current_app
from itsdangerous import TimedSerializer as Serializer

def generate_token(user, operation, expire_in=None, **kwargs):
    s = Serializer(current_app.config['SECRET_KEY'], expire_in) #生成token签名， expire_in过期时间，默认1小时
    data = {'id': user.id, 'operation': operation} # 把数据存储在字典里后续传入负载
    data.update(**kwargs)
    return s.dumps(data) # 写入数据生成头部
