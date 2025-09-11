import os
from datetime import datetime

from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from flask_avatars import Identicon

from albumy.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

# 用户模型类


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, index=True)
    email = db.Column(db.String(254), unique=True, index=True)
    name = db.Column(db.String(30))
    password_hash = db.Column(db.String(256))
    website = db.Column(db.String(128))
    location = db.Column(db.String(50))
    bio = db.Column(db.String(120))
    member_since = db.Column(db.DateTime, default=datetime.utcnow())
    confirm_statue = db.Column(db.Boolean, default=False)
    avatars_s = db.Column(db.String(64))
    avatars_m = db.Column(db.String(64))
    avatars_l = db.Column(db.String(64))
    roles_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    roles = db.relationship('Role', back_populates='users')
    photos = db.relationship('Photo', back_populates='auth', cascade='all')

    def set_hash(self, password):
        self.password_hash = generate_password_hash(password)

    def check_hash(self, password):
        return check_password_hash(self.password_hash, password)

    # 为用户设置角色
    def set_role(self):
        try:
            if self.roles is None:
                if self.email == current_app.config['MAIL_USERNAME']:
                    self.roles = Role.query.filter_by(
                        name='Administrator').first()
                else:
                    self.roles = Role.query.filter_by(name='User').first()
            db.session.commit()
        except Exception as e:
            db.session.rollback()

    # 生成随机头像
    def generate_avatars(self):
        avatar = Identicon()
        filename = avatar.generate(text=self.username)  # 以用户名作为文件名
        self.avatars_s = filename[0]  # 从生成小尺寸文件开始
        self.avatars_m = filename[1]
        self.avatars_l = filename[2]
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
    # 验证用户权限

    @property
    def is_admin(self):
        return self.roles.name == 'Administrator'

    def can(self, permission_name):
        permission = Permission.query.filter_by(name=permission_name).first()
        if permission in self.roles.permissions:
            return True
        return False

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.set_role()
        self.generate_avatars()

# 角色模型类


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, index=True)
    permissions = db.relationship(
        'Permission', secondary='Role_Permission', back_populates='roles')
    users = db.relationship('User', back_populates='roles')

    @staticmethod
    def init_role_permission():
        role_permission_map = {
            'Locked': ['COLLECT', 'FOLLOW'],
            'User': ['COLLECT', 'FOLLOW', 'COMMENT', 'UPLOAD'],
            'Moderate': ['COLLECT', 'FOLLOW', 'COMMENT', 'UPLOAD', 'MODERATE'],
            'Administrator': ['COLLECT', 'FOLLOW', 'COMMENT', 'UPLOAD', 'MODERATE', 'ADMINISTRATOR']
        }

        for role_name in role_permission_map:
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name)
                db.session.add(role)
                role.permissions = []
            for permission_name in role_permission_map[role_name]:
                permission = Permission.query.filter_by(
                    name=permission_name).first()
                if permission is None:
                    permission = Permission(name=permission_name)
                    db.session.add(permission)
                role.permissions.append(permission)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()

# 权限行为模型类


class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    roles = db.relationship(
        'Role', secondary='Role_Permission', back_populates='permissions')


# 关联表
Role_Permission = db.Table('Role_Permission',
                           db.Column('role_id', db.Integer,
                                     db.ForeignKey('role.id')),
                           db.Column('permission_id', db.Integer,
                                     db.ForeignKey('permission.id'))
                           )


# 访客类
class Guest(AnonymousUserMixin):
    @property
    def is_admin(self):
        return False

    def can(self, permission_name):
        return False

# 图片类


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(500))
    filename = db.Column(db.String(60))
    filename_s = db.Column(db.String(60))
    filename_m = db.Column(db.String(60))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    auth_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    auth = db.relationship('User', back_populates='photos')
    flag = db.Column(db.Integer, default=0)


@db.event.listens_for(Photo, 'after_delete', named=True)
def delete_photos(**kwargs):
    """为Photo模型创建事件监听事件，照片被删除了，对应文件夹的照片也要被删除"""
    target = kwargs['target']
    for filename in [target.filename, target.filename_s, target.filename_m]:
        if filename is not None:
            path = os.path.join(
                current_app.config['ALBUMY_UPLOAD_PATH'], filename)
            if os.path.exists(path):
                os.remove(path)
