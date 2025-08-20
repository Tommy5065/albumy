from functools import wraps

from flask import flash, redirect, Markup, url_for, abort
from flask_login import current_user

def confirm_required(func):
    @wraps(func)
    def decorate_confirm(*args, **kwargs):
        if not current_user.confirm_statue:
            message = Markup("You don't confirm your email"
                             "Please clink the link resend the email to verify"
                             '<a class="alert-link" href=%s>Resend the email</a>'
                             % url_for('auth.resend_confirm')
                             )
            flash(message,'warning')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    return decorate_confirm

# 权限查验装饰器
def permission_required(permission_name):
    def decorate(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission_name):
                abort(403)
            return func(*args, **kwargs)
        return decorated_function
    return decorate

# 管理员权限查验装饰器
def admin_required(func):
    permission_required('ADMINISTRATOR')(func)