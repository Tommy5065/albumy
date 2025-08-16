from datetime import datetime
from flask_login import UserMixin
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

    def set_hash(self, password):
        self.password_hash = generate_password_hash(password)

    def check_hash(self, password):
        return check_password_hash(self.password_hash, password)