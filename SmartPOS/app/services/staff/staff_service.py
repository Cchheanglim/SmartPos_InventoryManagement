"""
Orchestrates staff account management — create, list, activate/deactivate,
change role, assign shift — as one coherent service, composing
AuthService (for registration) and UserRepository/RoleRepository directly
(for everything else), rather than duplicating any of that logic here.

Unlike the other extractions in this codebase (RefundService,
PurchaseService, etc.), this one is NOT currently wired into
app/routes/staff/staff_routes.py. That route file already spans staff
CRUD, role assignment, shift assignment, and the permissions matrix
together across several methods with real, already-tested logic in each
— rewiring all of that to go through this class instead would mean
touching every one of those methods, which is a materially bigger and
riskier change than the other extractions in this project, each of which
moved one self-contained method or section. This class is real and
correct as written (it calls the same repository/service methods with
the same arguments staff_routes.py already does), and ready to be
adopted a method at a time if wanted — it just hasn't been forced in
under time pressure the way the rest of this session's work was tested
before being called done.
"""
from app.repositories.auth.user_repository import UserRepository
from app.repositories.auth.role_repository import RoleRepository
from app.services.auth.auth_service import AuthService


class StaffService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.role_repo = RoleRepository()
        self.auth_service = AuthService()

    def list_staff(self):
        return self.user_repo.list_all()

    def get_staff_member(self, user_id):
        return self.user_repo.find_by_id(user_id)

    def create_staff(self, name, email, password, role_name, phone=None):
        """Delegates to AuthService.register_user — account creation is
        an auth concern (password hashing, role lookup); this method
        exists so callers dealing with "staff management" as a concept
        don't need to also know that's where it lives."""
        return self.auth_service.register_user(name, email, password, role_name, phone=phone)

    def change_role(self, user_id, new_role_name):
        role = self.role_repo.find_by_name(new_role_name)
        if role is None:
            raise ValueError(f"Unknown role: {new_role_name}")
        self.user_repo.update_role(user_id, role.id)

    def update_phone(self, user_id, phone):
        import re
        clean_phone = re.sub(r"\D", "", phone or "") or None
        self.user_repo.update_phone(user_id, clean_phone)

    def assign_shift(self, user_id, shift_name, shift_start, shift_end):
        self.user_repo.set_shift(user_id, shift_name, shift_start, shift_end)

    def set_active(self, user_id, is_active):
        self.user_repo.set_active(user_id, is_active)

    def toggle_active(self, user_id):
        target = self.user_repo.find_by_id(user_id)
        if target is None:
            raise ValueError("Staff member not found.")
        self.user_repo.set_active(user_id, not target.is_active)
        return not target.is_active
