"""Flask application factory."""
import os
from flask import Flask, render_template, g
from flask_login import LoginManager

from app.config import Config
from app import extensions
from app.repositories.auth.user_repository import UserRepository


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["AVATAR_UPLOAD_FOLDER"], exist_ok=True)

    extensions.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    user_repo = UserRepository()

    @login_manager.user_loader
    def load_user(user_id):
        return user_repo.find_by_id(user_id)

    # ---- Real, implemented blueprints — routes stay thin; all logic lives in services. ----
    from app.routes.auth.auth_routes import auth_bp
    from app.routes.dashboard.dashboard_routes import dashboard_bp
    from app.routes.inventory.product_routes import products_bp
    from app.routes.inventory.category_routes import bp as category_bp
    from app.routes.inventory.supplier_routes import bp as supplier_bp
    from app.routes.sales.sales_routes import sales_bp
    from app.routes.reports.report_routes import reports_bp
    from app.routes.profile.profile_routes import profile_bp
    from app.routes.staff.staff_routes import staff_bp
    from app.routes.staff.attendance_routes import attendance_bp
    from app.routes.staff.task_routes import tasks_bp
    from app.routes.staff.shift_routes import bp as shift_bp
    from app.routes.notifications.notification_routes import bp as notification_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(category_bp, url_prefix="/categories")
    app.register_blueprint(supplier_bp, url_prefix="/suppliers")
    app.register_blueprint(sales_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(shift_bp, url_prefix="/shifts")
    app.register_blueprint(notification_bp, url_prefix="/notifications")

    # ---- Not-yet-built modules — still a placeholder blueprint so the
    # folder structure is complete and the app boots, but nothing behind
    # this is real yet. A generic catch-all inventory dashboard/overview
    # page — product, category, supplier, and stock management already
    # have their own real pages above. ----
    from app.routes.inventory.inventory_routes import bp as inventory_bp

    app.register_blueprint(inventory_bp, url_prefix="/inventory")

    @app.template_global()
    def category_icon(category_name):
        """
        Looks up the icon a category was actually configured with (see
        CategoryService — admins pick this from a curated dropdown when
        creating/editing a category), falling back to a generic box for
        anything not found (e.g. a product whose category was set before
        that category existed, or free-typed).

        Cached on flask.g for the lifetime of the request — this can be
        called once per row in a product list, and every call after the
        first reuses the same lookup instead of re-querying MySQL.
        """
        if "category_icon_map" not in g:
            from app.services.inventory.category_service import CategoryService
            g.category_icon_map = {c.name: c.icon for c in CategoryService().list_categories()}
        from app.models.inventory.category import Category
        return g.category_icon_map.get(category_name, Category.DEFAULT_ICON)

    @app.template_global()
    def format_shift_time(value):
        """
        MySQL TIME columns come back from PyMySQL as datetime.timedelta
        (not datetime.time), which prints as '8:0:0' — this normalizes
        any of timedelta / time / 'HH:MM:SS' string into a clean 'HH:MM'
        that both displays correctly and is valid for <input type="time">.
        """
        if value is None:
            return ""
        if isinstance(value, str):
            parts = value.split(":")
            return f"{int(parts[0]):02d}:{int(parts[1]):02d}"
        total_seconds = int(value.total_seconds()) if hasattr(value, "total_seconds") else (
            value.hour * 3600 + value.minute * 60
        )
        hours = (total_seconds // 3600) % 24
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"

    @app.context_processor
    def inject_permissions():
        from flask_login import current_user
        from app.services.auth.auth_service import AuthService
        from app.services.notifications.notification_service import NotificationService
        if current_user.is_authenticated:
            return {
                "permissions": AuthService().get_permissions_for_user(current_user),
                "unread_notification_count": NotificationService().count_unread(current_user.id),
            }
        return {"permissions": set(), "unread_notification_count": 0}

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("500.html"), 500

    return app
