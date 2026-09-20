"""
No separate RolePermission class exists because role_permissions is a
plain many-to-many junction table (role_id, permission_id) — see
sql/schema.sql. It's read and written directly as sets of IDs/names by
RoleRepository/PermissionRepository (app/repositories/auth/role_repository.py:
list_for_role, set_role_permissions), which is all this junction table is
ever used for — there's no scenario where a single row needs its own
identity or behavior beyond "does this pairing exist."

Wrapping that in a RolePermission object would add an unused layer
between the repository and the sets/ids callers actually want, so this
file intentionally has no class.
"""
