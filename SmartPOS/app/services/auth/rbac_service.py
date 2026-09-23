"""
RBACService: Owns all validation, policy decisions, and security safeguards
for dynamic Role-Based Access Control (RBAC).

Adheres to strict layered architecture:
    Routes -> RBACService -> RoleRepository / PermissionRepository / UserRepository -> MySQL
"""
import re
from app.repositories.auth.role_repository import RoleRepository, PermissionRepository
from app.repositories.auth.user_repository import UserRepository


class RBACService:
    """
    Central business service managing runtime roles, permissions, matrix associations,
    and user role assignments with bulletproof administrative safeguards.
    """

    # Protected system permissions referenced in @permission_required(...) decorators
    # in application routes. These cannot be deleted from the database because doing so
    # would make the associated route permanently unreachable for all users.
    SYSTEM_PERMISSIONS = {
        "manage_roles": "Access and manage roles, permissions, and security matrix",
        "manage_users": "Create and manage staff accounts, shifts, and credentials",
        "manage_products": "Create, edit, and archive inventory products and categories",
        "adjust_stock": "Perform stock adjustments and audit stock movements",
        "process_sale": "Operate the POS register, barcode scanner, and checkout",
        "process_refund": "Authorize and process customer refunds on past invoices",
        "view_reports": "Access financial analytics, business health, and CRM reports",
        "manage_cashier_accounts": "Review cashier shift balances and registers",
    }

    def __init__(self):
        self.role_repo = RoleRepository()
        self.permission_repo = PermissionRepository()
        self.user_repo = UserRepository()
        self.ensure_bootstrapped_system_permissions()

    def ensure_bootstrapped_system_permissions(self):
        """
        Idempotently verifies that system permissions (especially manage_roles)
        exist in the database and are granted to the 'admin' role.
        """
        for name, desc in self.SYSTEM_PERMISSIONS.items():
            self.permission_repo.ensure_permission_exists(name, desc, default_role_name="admin")

    # -------------------------------------------------------------------------
    # Role Operations
    # -------------------------------------------------------------------------

    def list_roles(self):
        """Returns all roles along with their current user assignment counts."""
        return self.role_repo.list_with_user_counts()

    def get_role(self, role_id):
        role = self.role_repo.find_by_id(role_id)
        if not role:
            raise ValueError(f"Role ID #{role_id} not found.")
        return role

    def create_role(self, name):
        """
        Creates a new role with strict validation.
        """
        clean_name = self._validate_name(name, entity_type="Role")
        clean_key = clean_name.lower().replace(" ", "_")

        if self.role_repo.find_by_name(clean_key):
            raise ValueError(f"A role with the name '{clean_name}' already exists.")

        return self.role_repo.create(clean_key)

    def rename_role(self, role_id, new_name):
        """
        Renames an existing role. Prevents renaming the core 'admin' role.
        """
        role = self.get_role(role_id)
        clean_name = self._validate_name(new_name, entity_type="Role")
        clean_key = clean_name.lower().replace(" ", "_")

        if role.name == "admin" and clean_key != "admin":
            raise ValueError("The core 'admin' role cannot be renamed as system components rely on it.")

        existing = self.role_repo.find_by_name(clean_key)
        if existing and existing.id != role_id:
            raise ValueError(f"Another role with the name '{clean_name}' already exists.")

        self.role_repo.update(role_id, clean_key)

    def delete_role(self, role_id):
        """
        Deletes a role from the system, enforcing all required safeguards:
        1. Cannot delete the core 'admin' role.
        2. Cannot delete a role that still has users assigned to it.
        3. Cannot leave zero roles holding 'manage_roles' permission.
        """
        role = self.get_role(role_id)

        # Safeguard 1: Protect 'admin' role
        if role.name.lower() == "admin":
            raise ValueError("The 'admin' role cannot be deleted as it is vital to system governance.")

        # Safeguard 2: Check assigned users
        user_count = self.role_repo.count_users_with_role(role_id)
        if user_count > 0:
            raise ValueError(
                f"Cannot delete role '{role.display_name}' because {user_count} staff member(s) "
                f"are currently assigned to it. Please reassign those users to another role first."
            )

        # Safeguard 3: Prevent locking out manage_roles
        roles_with_manage = self.role_repo.roles_with_permission("manage_roles")
        if len(roles_with_manage) == 1 and roles_with_manage[0].id == role_id:
            raise ValueError(
                "Access Control Safeguard: This role is the only role holding the 'manage_roles' permission. "
                "Deleting it would permanently lock all users out of managing roles and permissions."
            )

        self.role_repo.delete(role_id)

    # -------------------------------------------------------------------------
    # Permission Operations
    # -------------------------------------------------------------------------

    def list_permissions(self):
        """
        Returns all permissions, marking system permissions and injecting default descriptions.
        """
        perms = self.permission_repo.list_all()
        for p in perms:
            if p.name in self.SYSTEM_PERMISSIONS:
                p.is_system = True
                if not p.description or p.description == p.name.replace("_", " ").title():
                    p.description = self.SYSTEM_PERMISSIONS[p.name]
        return perms

    def get_permission(self, permission_id):
        perm = self.permission_repo.find_by_id(permission_id)
        if not perm:
            raise ValueError(f"Permission ID #{permission_id} not found.")
        if perm.name in self.SYSTEM_PERMISSIONS:
            perm.is_system = True
            perm.description = self.SYSTEM_PERMISSIONS[perm.name]
        return perm

    def create_permission(self, name, description=None):
        """
        Creates a new custom permission.
        """
        clean_name = self._validate_name(name, entity_type="Permission")
        clean_key = clean_name.lower().replace(" ", "_")

        if self.permission_repo.find_by_name(clean_key):
            raise ValueError(f"A permission with the name '{clean_name}' already exists.")

        clean_desc = (description or "").strip() or clean_name.replace("_", " ").title()
        return self.permission_repo.create(clean_key, clean_desc)

    def rename_permission(self, permission_id, new_name, description=None):
        """
        Renames a custom permission. Protects system permissions from renaming.
        """
        perm = self.get_permission(permission_id)

        if perm.name in self.SYSTEM_PERMISSIONS:
            raise ValueError(
                f"Cannot rename '{perm.name}': This is a system permission referenced directly "
                f"by application route security decorators (@permission_required)."
            )

        clean_name = self._validate_name(new_name, entity_type="Permission")
        clean_key = clean_name.lower().replace(" ", "_")

        existing = self.permission_repo.find_by_name(clean_key)
        if existing and existing.id != permission_id:
            raise ValueError(f"Another permission with the name '{clean_name}' already exists.")

        clean_desc = (description or "").strip() or perm.description
        self.permission_repo.update(permission_id, clean_key, clean_desc)

    def delete_permission(self, permission_id):
        """
        Deletes a permission. Protects system permissions from deletion.
        """
        perm = self.get_permission(permission_id)

        if perm.name in self.SYSTEM_PERMISSIONS:
            raise ValueError(
                f"Cannot delete '{perm.name}': This is a system permission required by route "
                f"security decorators (@permission_required). Deleting it would break route access."
            )

        self.permission_repo.delete(permission_id)

    # -------------------------------------------------------------------------
    # Role x Permission Matrix Operations
    # -------------------------------------------------------------------------

    def get_matrix_data(self):
        """
        Returns full data required to render the Role x Permission matrix.
        """
        roles = self.list_roles()
        all_permissions = self.list_permissions()
        current_map = {role.id: self.permission_repo.list_permission_ids_for_role(role.id) for role in roles}

        manage_roles_perm = next((p for p in all_permissions if p.name == "manage_roles"), None)
        manage_roles_id = manage_roles_perm.id if manage_roles_perm else None

        return {
            "roles": roles,
            "all_permissions": all_permissions,
            "current": current_map,
            "manage_roles_id": manage_roles_id,
        }

    def save_matrix(self, role_permissions_map):
        """
        Atomically saves the entire role x permission matrix.

        Tradeoff Note:
        Saving the entire matrix via a single "Save Permissions" submission is chosen
        over live single-checkbox AJAX because it enables holistic, atomic safeguard
        validation across all roles before anything is committed to MySQL. If an admin
        accidentally unticks 'manage_roles' from all roles, the entire batch is rejected
        in memory and no database writes occur, preventing accidental lockouts.

        :param role_permissions_map: dict of {role_id: set_of_permission_ids}
        """
        all_permissions = self.list_permissions()
        manage_roles_perm = next((p for p in all_permissions if p.name == "manage_roles"), None)

        if manage_roles_perm:
            # Safeguard: At least one role must retain 'manage_roles'
            has_manage_roles = any(
                manage_roles_perm.id in pids for pids in role_permissions_map.values()
            )
            if not has_manage_roles:
                raise ValueError(
                    "Access Control Safeguard: At least one role must retain the 'manage_roles' "
                    "permission to prevent permanent administrative lockout."
                )

        # Save each role's permissions
        for role_id, permission_ids in role_permissions_map.items():
            self.permission_repo.set_role_permissions(role_id, permission_ids)

    # -------------------------------------------------------------------------
    # User Role Assignment
    # -------------------------------------------------------------------------

    def assign_user_role(self, user_id, role_id, acting_user_id=None):
        """
        Assigns a user to a specific role. Protects against demoting the sole active admin.
        """
        target_user = self.user_repo.find_by_id(user_id)
        if not target_user:
            raise ValueError(f"User ID #{user_id} not found.")

        target_role = self.get_role(role_id)

        # Protect against self-demoting from admin if acting user is this user
        if acting_user_id and target_user.id == acting_user_id and target_user.role_name == "admin" and target_role.name != "admin":
            # Check how many active admins exist
            admins = [u for u in self.user_repo.list_all() if u.role_name == "admin" and u.is_active]
            if len(admins) <= 1:
                raise ValueError("You cannot demote yourself from Admin because you are the only active Administrator.")

        self.user_repo.update_role(user_id, target_role.id)

    # -------------------------------------------------------------------------
    # Helper Validation
    # -------------------------------------------------------------------------

    def _validate_name(self, name, entity_type="Role"):
        if not name or not str(name).strip():
            raise ValueError(f"{entity_type} name cannot be empty.")
        clean = str(name).strip()
        if len(clean) < 2 or len(clean) > 50:
            raise ValueError(f"{entity_type} name must be between 2 and 50 characters.")
        if not re.match(r"^[A-Za-z0-9_\-\s]+$", clean):
            raise ValueError(f"{entity_type} name can only contain letters, numbers, spaces, underscores, and hyphens.")
        return clean
