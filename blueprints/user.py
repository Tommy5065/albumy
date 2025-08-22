from flask import Blueprint, render_template, request, current_app
from flask_login import login_required

from albumy.models import User, Photo

bp = Blueprint('user', __name__)

@bp.route('/index/<username>')
def index(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config["ALBUMY_IMAGE_PER_PAGE"]
    pagination = Photo.query.with_parent(user).order_by(Photo.timestamp.desc()).paginate(page=page, per_page=per_page)
    photos = pagination.items
    return render_template('users/_header.html', user=user, photos=photos, pagination=pagination)