import re
from werkzeug.security import generate_password_hash, check_password_hash
from app.repositories.auth.user_repository import UserRepository
from app.repositories.auth.role_repository import RoleRepository, PermissionRepository
from app.services.auth.permission_service import PermissionService
from app.services.auth.password_reset_service import PasswordResetService


class AuthService:
    """
    Owns every RBAC decision in the system. The database stores and
    relates roles/permissions data, but this service is what actually
    decides whether a user is allowed to do something.

    Permission resolution and password-reset are delegated to
    PermissionService/PasswordResetService respectively (see those files)
    — this class keeps the same public methods everything else already
    calls, just implemented via composition instead of inline.
    """

    def __init__(self):
        self.user_repo = UserRepository()
        self.role_repo = RoleRepository()
        self.permission_repo = PermissionRepository()
        self.permission_service = PermissionService()
        self.password_reset_service = PasswordResetService()

    def authenticate(self, email, password):
        """Returns the User if credentials are valid and the account is active, else None."""
        user = self.user_repo.find_by_email(email)
        if user is None or not user.is_active:
            return None
        if not check_password_hash(user.password_hash, password):
            return None
        return user

    def register_user(self, name, email, password, role_name, phone=None):
        role = self.role_repo.find_by_name(role_name)
        if role is None:
            raise ValueError(f"Unknown role: {role_name}")
        password_hash = generate_password_hash(password)
        clean_phone = self._clean_phone(phone) or None
        return self.user_repo.create(name, email, password_hash, role.id, phone=clean_phone)

    @staticmethod
    def _clean_phone(phone):
        return re.sub(r"\D", "", phone or "")

    def change_password(self, user, current_password, new_password):
        """Self-service password change — requires the user's current
        password to prevent someone from hijacking an unattended session."""
        if not check_password_hash(user.password_hash, current_password):
            raise ValueError("Current password is incorrect.")
        if len(new_password) < 6:
            raise ValueError("New password must be at least 6 characters.")
        self.user_repo.update_password_hash(user.id, generate_password_hash(new_password))

    def request_password_reset(self, phone):
        self.password_reset_service.request_password_reset(phone, self._clean_phone)

    def verify_reset_token(self, raw_token):
        """Returns the User if raw_token is valid and unexpired, else None."""
        return self.password_reset_service.verify_reset_token(raw_token)

    def reset_password(self, raw_token, new_password):
        """Completes a reset. Raises ValueError on an invalid/expired
        token or a too-short password."""
        self.password_reset_service.reset_password(raw_token, new_password)

    def get_permissions_for_user(self, user):
        """
        A user's real permission set is their role's permissions PLUS
        anything an Admin has individually granted them.
        """
        return self.permission_service.get_permissions_for_user(user)

    def has_permission(self, user, permission_name):
        return self.permission_service.has_permission(user, permission_name)
