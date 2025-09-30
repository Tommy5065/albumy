import os
from flask import Blueprint, render_template, request, current_app, send_from_directory, flash, redirect, url_for, abort
from flask_login import login_required, current_user

from albumy.utils import random_filename, resize_image
from albumy.decorators import confirm_required, permission_required
from albumy.models import Photo, Tag, Comment, User
from albumy.extensions import db

from forms.user import DescriptionForm, TagForm, CommentForm

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
    try:
        if request.method == 'POST' and 'file' in request.files:
            file = request.files.get('file')
            filename = file.filename
            new_filename = random_filename(filename=filename)
            file.save(os.path.join(
                current_app.config['ALBUMY_UPLOAD_PATH'], new_filename))
            filename_s = resize_image(file, new_filename, 400)
            filename_m = resize_image(file, new_filename, 800)

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


@bp.route('/avatars/<path:filename>')
def get_avatar(filename):
    """生成像static视图函数一样的资源指向"""
    return send_from_directory(current_app.config["AVATARS_SAVE_PATH"], filename)


@bp.route('/get_image/<path:filename>')
def get_image(filename):
    """获取图片资源"""
    return send_from_directory(current_app.config['ALBUMY_UPLOAD_PATH'], filename)


@bp.route('/explore')
def explore():
    return render_template('main/explore.html')


@bp.route('/photo/<int:photo_id>')
@permission_required('COMMENT')
def show_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    description_form = DescriptionForm()
    tag_form = TagForm()
    comment_form = CommentForm()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ALBUMY_COMMENT_PER_PAGE']
    pagination = Comment.query.with_parent(photo).order_by(
        Comment.timestamp.desc()).paginate(page=page, per_page=per_page)
    comments = pagination.items

    description_form.description.data = photo.description
    return render_template('users/photo.html', photo=photo, description_form=description_form, tag_form=tag_form, comment_form=comment_form, comments=comments)


@bp.route('/photo/n/<int:photo_id>')
def photo_next(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    photo_n = Photo.query.with_parent(photo.auth).filter(
        Photo.id > photo.id).order_by(Photo.timestamp.asc()).first()
    if photo_n is None:
        flash('This is latest picture', 'info')
        return redirect(url_for('.show_photo', photo_id=photo.id))

    return redirect(url_for('.show_photo', photo_id=photo_n.id))


@bp.route('/photo/p/<int:photo_id>')
def photo_previous(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    photo_p = Photo.query.with_parent(photo.auth).filter(
        Photo.id < photo.id).order_by(Photo.timestamp.desc()).first()
    if photo_p is None:
        flash('This is already first one', 'info')
        return redirect(url_for('.show_photo', photo_id=photo.id))

    return redirect(url_for('.show_photo', photo_id=photo_p.id))


@bp.route('/photo_delete/<int:photo_id>', methods=['POST', 'GET'])
def photo_delete(photo_id):
    if request.method == 'POST':
        photo = Photo.query.first_or_404(photo_id)
        if current_user != photo.auth:
            abort(404)
        try:
            db.session.delete(photo)
            db.session.commit()
            flash('Delete photo successfully', 'successful')
        except Exception:
            db.session.rollback()

        # 删除图片后切换成下一张图片的详情页
        photo_n = Photo.query.with_parent(photo.auth).filter(
            Photo.id > photo.id).order_by(Photo.timestamp.asc()).first()
        if photo_n is None:
            # 如果没有下一张了就切换成上一张的详情页
            photo_p = Photo.query.with_parent(photo.auth).filter(
                Photo.id < photo.id).order_by(Photo.timestamp.desc()).first()
            if photo_p is None:
                # 上一张也没有就返回主页
                return redirect(url_for('user.index', username=photo.auth.username))
            return redirect(url_for('.show_photo', photo_id=photo_p.id))

        return redirect(url_for('.show_photo', photo_id=photo_n.id))


@bp.route('/report/photo/<int:photo_id>', methods=['POST'])
@confirm_required
def report_photo(photo_id):
    """记录图片被举报次数 """
    photo = Photo.query.get_or_404(photo_id)
    photo.flag = (photo.flag or 0)+1
    db.session.commit()
    flash("report photo success", 'success')
    return redirect(url_for('.show_photo', photo_id=photo.id))


@bp.route('/photo/<int:photo_id>/description', methods=['POST'])
@confirm_required
def edit_description(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if current_user != photo.auth:
        abort(403)

    form = DescriptionForm()
    if form.validate_on_submit:
        photo.description = form.description.data
        db.session.commit()
        flash('description photo success!', 'successful')

    return redirect(url_for('.show_photo', photo_id=photo.id))


@bp.route('/photo/<int:photo_id>/tag', methods=['POST'])
@confirm_required
def new_tag(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if current_user != photo.auth:
        abort(403)

    form = TagForm()
    if form.validate_on_submit:
        for name in form.tag.data.split():
            tag = Tag.query.filter_by(tag=name).first()
            if tag is None:
                tag = Tag(tag=name)
                db.session.add(tag)

            if tag not in photo.tags:
                photo.tags.append(tag)

            db.session.commit()
        flash('add tag successful!', 'successful')

    return redirect(url_for('.show_photo', photo_id=photo.id))


@bp.route('/delete/tag/<int:tag_id>/<int:photo_id>')
@confirm_required
def delete_tag(tag_id, photo_id):
    tag = Tag.query.get_or_404(tag_id)
    photo = Photo.query.get_or_404(photo_id)
    if current_user != photo.auth:
        abort(403)

    photo.tags.remove(tag)
    db.session.commit

    if not tag.photos:
        db.session.delete(tag)
        db.session.commit()
    flash('Delete tag successful!', 'info')
    return redirect(url_for('.show_photo', photo_id=photo.id))


@bp.route('/tag/<int:tag_id>', defaults={'order': 'time'})
@bp.route('/tag/<int:tag_id>/<order>')
def show_tag(tag_id, order):
    tag = Tag.query.get_or_404(tag_id)
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config['ALBUMY_IMAGE_PER_PAGE']
    pagination = Photo.query.with_parent(tag).order_by(
        Photo.timestamp.asc()).paginate(page=page, per_page=per_page)
    photos = pagination.items
    order_rule = 'by_time'

    if order == 'by_collects':
        # 本来是以收藏者数量为排序，但是没有做collects这个字段，所以暂时用flag数字字段来代替
        # .sort()是图片的排序方式
        photos.sort(key=lambda x: x.flag, reverse=True)
        order_rule = 'by_collects'
    return render_template('main/tag.html', pagination=pagination, photos=photos, order_rule=order_rule, tag=tag)


@bp.route('/comment/new_comment/<int:photo_id>', methods=['POST'])
def new_comment(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    user = User.query.get_or_404(current_user.id)

    form = CommentForm()
    if form.validate_on_submit:
        body = form.body.data
        comment = Comment(name=current_user.username, body=body)
        photo.comments.append(comment)
        user.comments.append(comment)
        db.session.add(comment)
        db.session.commit()
    flash('Thanks for your comments!', 'info')
    return redirect(url_for('.show_photo', photo_id=photo.id))


@bp.route('/comment/delete_comment/<int:photo_id>/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id, photo_id):
    photo = Photo.query.get_or_404(photo_id)
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Delete comment successful!', 'info')
    return redirect(url_for('.show_photo', photo_id=photo.id))


@bp.route('/comment/report_comment/<int:photo_id>/<int:comment_id>', methods=['POST'])
@confirm_required
def report_comment(photo_id, comment_id):
    photo = Photo.query.get_or_404(photo_id)
    comment = Comment.query.get_or_404(comment_id)
    comment.flag += 1
    db.session.commit()
    flash('report comment successful', 'info')
    return redirect(url_for('.show_photo', photo_id=photo.id))


@bp.route('/comment/reply_comment/<int:comment_id>')
@confirm_required
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    return redirect(url_for('.show_photo', photo_id=comment.photo.id, reply=comment.id, auth=comment.author.name)+"#comment-form")
