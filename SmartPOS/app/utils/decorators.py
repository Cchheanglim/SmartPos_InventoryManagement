"""
Single reusable RBAC enforcement point for every protected route.

Any route that needs a permission check uses @permission_required(...),
so the check happens in exactly one place and behaves identically
everywhere it is applied — this is what Section 13 of the proposal's
risk table refers to as "a single role-check pattern across all routes."
"""
from functools import wraps
from flask import abort
from flask_login import current_user

from app.services.auth.auth_service import AuthService

auth_service = AuthService()


def permission_required(permission_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not auth_service.has_permission(current_user, permission_name):
                abort(403)
            return view_func(*args, **kwargs)
        return wrapper
    return decorator
