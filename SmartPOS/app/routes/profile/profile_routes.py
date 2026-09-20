import os
import re
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.repositories.auth.user_repository import UserRepository
from app.services.auth.auth_service import AuthService

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")
user_repo = UserRepository()
auth_service = AuthService()


def _allowed_file(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]


@profile_bp.route("/", methods=["GET", "POST"])
@login_required
def my_profile():
    if request.method == "POST":
        file_storage = request.files.get("avatar")
        if file_storage and file_storage.filename:
            if not _allowed_file(file_storage.filename):
                flash("Avatar must be PNG, JPG, JPEG, GIF, or WEBP.", "error")
                return redirect(url_for("profile.my_profile"))
            ext = file_storage.filename.rsplit(".", 1)[-1].lower()
            safe_name = secure_filename(f"{uuid.uuid4().hex}.{ext}")
            file_storage.save(os.path.join(current_app.config["AVATAR_UPLOAD_FOLDER"], safe_name))
            user_repo.update_profile_picture(current_user.id, safe_name)
            flash("Profile picture updated.", "success")
            return redirect(url_for("profile.my_profile"))
        flash("No file selected.", "error")
    return render_template("auth/profile.html")


@profile_bp.route("/update-info", methods=["POST"])
@login_required
def update_info():
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    clean_phone = re.sub(r"\D", "", phone) or None

    if not name:
        flash("Name cannot be empty.", "error")
        return redirect(url_for("profile.my_profile"))

    try:
        user_repo.update_name(current_user.id, name)
        user_repo.update_phone(current_user.id, clean_phone)
        flash("Profile updated.", "success")
    except Exception:
        # e.g. another account already has this phone number — MySQL
        # raises IntegrityError on the UNIQUE constraint, not ValueError
        flash("Could not update — that phone number may already be in use.", "error")
    return redirect(url_for("profile.my_profile"))


@profile_bp.route("/change-password", methods=["POST"])
@login_required
def change_password():
    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    if new_password != confirm_password:
        flash("New password and confirmation do not match.", "error")
        return redirect(url_for("profile.my_profile"))

    try:
        auth_service.change_password(current_user, current_password, new_password)
        flash("Password updated successfully.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("profile.my_profile"))
