"""
Owns permission resolution, extracted from AuthService.get_permissions_for_user
/has_permission. AuthService still exposes those same two method names
(everything that calls them — the permission_required decorator, the
navbar's permission checks, staff_routes.py — is unchanged) and just
delegates to this internally, so RBAC decision-making has its own single
responsibility separate from authentication/registration.
"""
from app.repositories.auth.role_repository import PermissionRepository


class PermissionService:
    def __init__(self):
        self.permission_repo = PermissionRepository()

    def get_permissions_for_user(self, user):
        """
        A user's real permission set is their role's permissions PLUS
        anything an Admin has individually granted them — individual
        grants only ever add, never remove what the role already allows.
        """
        role_perms = self.permission_repo.list_for_role(user.role_id)
        extra_perms = self.permission_repo.list_extra_permission_names_for_user(user.id)
        return role_perms | extra_perms

    def has_permission(self, user, permission_name):
        if user is None or not user.is_active:
            return False
        return permission_name in self.get_permissions_for_user(user)
