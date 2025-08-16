from flask import Blueprint, render_template, redirect, flash,url_for
from flask_login import current_user
from forms.auth import RegisterForm
from albumy.models import User
from albumy.extensions import db
from albumy.emails import send_confirm_email
from albumy.settings import Operations
from albumy.utils import generate_token

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