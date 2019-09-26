# 检查用户权限的自定义装饰器
from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission


def permission_required(permission):        # 检查常规权限
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):          # 检查管理员权限
    return permission_required(Permission.ADMIN)(f)
