"""
No separate UserPermission class exists because user_permissions is a
many-to-many junction table (user_id, permission_id, granted_by,
granted_at) — see sql/schema.sql — for individual permission grants on
top of a user's role. It's read and written directly as sets of IDs by
PermissionRepository (app/repositories/auth/role_repository.py:
list_extra_permission_ids_for_user, set_user_permissions), the same way
role_permissions is (see role_permission.py in this folder).

This file intentionally has no class for the same reason: wrapping a
junction row in an object would add a layer nothing currently needs.
"""
