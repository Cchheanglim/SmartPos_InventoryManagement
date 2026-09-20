from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from app.services.auth.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)
auth_service = AuthService()


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        user = auth_service.authenticate(email, password)
        if user is None:
            flash("Invalid email or password.", "error")
            return render_template("auth/login.html")
        login_user(user)
        return redirect(url_for("dashboard.index"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        auth_service.request_password_reset(phone)
        # Same message no matter what — never reveal whether that phone
        # number is actually registered.
        flash(
            "If that phone number is registered, a reset link has been sent to "
            "the shop's Telegram chat. It expires in 15 minutes.",
            "info",
        )
        return redirect(url_for("auth.login"))

    return render_template("auth/forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    user = auth_service.verify_reset_token(token)
    if user is None:
        flash("This reset link is invalid or has expired. Request a new one below.", "error")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")
        if new_password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("auth/reset_password.html", token=token)
        try:
            auth_service.reset_password(token, new_password)
        except ValueError as e:
            flash(str(e), "error")
            return render_template("auth/reset_password.html", token=token)
        flash("Password reset — you can log in with your new password now.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", token=token)
