from flask import abort
from functools import wraps

from flask_login import current_user


def staff_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if not current_user.is_staff:
            abort(403)
        return func(*args, **kwargs)

    return decorated


def professor_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if current_user.is_student:
            abort(403)
        return func(*args, **kwargs)

    return decorated


def student_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if not current_user.is_student:
            abort(403)
        return func(*args, **kwargs)

    return decorated
