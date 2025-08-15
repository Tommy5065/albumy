from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap


# login_manager = LoginManager()
csrf = CSRFProtect()
moment = Moment()
db = SQLAlchemy()
bootstrap = Bootstrap()