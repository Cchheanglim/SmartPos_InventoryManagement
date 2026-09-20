"""
Real WTForms validator for individual permission overrides
(app/routes/staff/staff_routes.py, user_permissions route) — granting one
specific user extra permissions beyond what their role already gives them.

The separate role-vs-permission MATRIX form (staff/permissions.html) posts
one dynamically-named checkbox list per role (`role_<role_id>`, since the
number of roles is data, not fixed at code time) — that shape isn't
expressible as a static WTForms field, so it's validated directly in
staff_routes.permissions_matrix() instead, the same way refund line items
are (see forms/refund_forms.py).
"""
from flask_wtf import FlaskForm
from wtforms import SelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput


class UserPermissionOverrideForm(FlaskForm):
    extra_permissions = SelectMultipleField(
        "Extra Permissions", coerce=int,
        widget=ListWidget(prefix_label=False), option_widget=CheckboxInput(),
    )

    def __init__(self, *args, permission_choices=None, **kwargs):
        """permission_choices: list of (permission_id, permission_name) tuples,
        fetched from PermissionRepository.list_all() at request time —
        WTForms SelectField choices can't be class-level since they depend
        on what's currently in the database."""
        super().__init__(*args, **kwargs)
        self.extra_permissions.choices = permission_choices or []
