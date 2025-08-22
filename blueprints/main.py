import os
from flask import Blueprint, render_template, request, current_app
from flask_login import login_required, current_user

from albumy.utils import random_filename, resize_image
from albumy.decorators import confirm_required, permission_required
from albumy.models import Photo
from albumy.extensions import db
bp = Blueprint('main', __name__)

@bp.before_request
@login_required
def login():
    pass

@bp.route('/')
def index():
    return render_template('main/index.html')

@bp.route('/upload', methods=['POST', 'GET'])
@confirm_required
@permission_required('UPLOAD')
def upload():
    if request.method == 'POST' and 'file' in request.files:
        file = request.files.get('file')
        filename = file.filename
        new_filename = random_filename(filename=filename)
        file.save(os.path.join(current_app.config['ALBUMY_UPLOAD_PATH'], new_filename))
        filename_s = resize_image(file, new_filename, 400)
        filename_m = resize_image(file, new_filename, 800)
    try:
        photo = Photo(
            filename=new_filename,
            filename_s=filename_s,
            filename_m=filename_m,
            auth=current_user
        )
        db.session.add(photo)
        db.session.commit()
    except Exception:
        db.session.rollback()

    return render_template('main/upload.html')