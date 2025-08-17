from functools import wraps

from flask import flash, redirect, Markup, url_for
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