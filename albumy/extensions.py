from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap4
from flask_mail import Mail
from flask_dropzone import Dropzone

login_manager = LoginManager()
csrf = CSRFProtect()
moment = Moment()
db = SQLAlchemy()
bootstrap = Bootstrap4()
mail = Mail()
dropzone = Dropzone()

@login_manager.user_loader
def user_loader(user_id):
    from albumy.models import User
    user = User.query.get(int(user_id))
    return user
