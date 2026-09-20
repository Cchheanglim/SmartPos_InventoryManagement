"""
Run once after schema.sql to create one demo login per role.
    python seed_users.py

All demo accounts use the password: password123
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.services.auth.auth_service import AuthService

app = create_app()
auth_service = AuthService()

DEMO_USERS = [
    ("Admin User", "admin@smartpos.local", "admin"),
    ("Assistant User", "assistant@smartpos.local", "admin_assistant"),
    ("Inventory User", "inventory@smartpos.local", "inventory_manager"),
    ("Cashier User", "cashier@smartpos.local", "cashier"),
]

with app.app_context():
    for name, email, role_name in DEMO_USERS:
        try:
            auth_service.register_user(name, email, "password123", role_name)
            print(f"Created {role_name}: {email}")
        except Exception as e:
            print(f"Skipped {email}: {e}")
