from flask import Blueprint, render_template, redirect, flash,url_for
from flask_login import current_user, login_required, login_user, logout_user
from forms.auth import RegisterForm, LoginForm
from albumy.models import User
from albumy.extensions import db
from albumy.emails import send_confirm_email
from albumy.settings import Operations
from albumy.utils import generate_token, validate_token, redirect_up

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect('main.index')

    form = RegisterForm()

    if form.validate_on_submit():
        name = form.Name.data
        email = form.Email.data.lower()
        username = form.Username.data
        password = form.Password.data
        user = User(username=username, email=email, name=name)
        user.set_hash(password)
        db.session.add(user)
        db.session.commit()
        token = generate_token(user=user, operation=Operations.CONFIRM)
        send_confirm_email(user=user, token=token)
        flash('Send confirm email, check your inbox', 'info')
        return redirect(url_for('.login'))

    return render_template('auth/register.html', form=form)

@bp.route('/confirm/<token>')
@login_required
def confirm(token):
    """
    检验Token令牌
    :param token: 邮件中的长传随机字符串
    :return:
    """
    if current_user.confirm_statue:
        return redirect(url_for('main.index'))

    if validate_token(user=current_user, token=token, operation=Operations.CONFIRM):
        flash('Account confirmed!','success')
        return redirect(url_for('main'))
    else:
        flash('Invalid or expired token','warning')
        return redirect(url_for('.resend_confirm'))

@bp.route('/resend_confirm_email')
@login_required
def resend_confirm():
    if current_user.confirm_statue:
        return redirect(url_for('main.index'))

    token = generate_token(user=current_user, operation=Operations.CONFIRM)
    send_confirm_email(user=current_user, token=token)
    flash('Resend email in your inbox','info')
    return redirect(url_for('main.index'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.Email.data.lower()).first()
        if user is not None and user.check_hash(form.Password.data):
            if login_user(user,form.Remember_Me.data):
                flash('login successfully', 'success')
                return redirect_up()
            else:
                flash('Your is blocked!','warning')
                return redirect(url_for('main.index'))

        flash('Invalid Email or password','warning')
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout Successfully!','success')
    return redirect_up()
