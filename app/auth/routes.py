"""Authentication routes: register, login, logout."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.auth.forms import LoginForm, RegisterForm
from app.extensions import db
from app.models import User, UserRole
from app.utils import flash_form_errors

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Show the sign-up form and create a citizen account."""
    if current_user.is_authenticated:
        return redirect(url_for("citizen.dashboard"))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            full_name=form.full_name.data.strip(),
            email=form.email.data.strip().lower(),
            role=UserRole.CITIZEN,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))

    flash_form_errors(form)
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Verify credentials and start a session."""
    if current_user.is_authenticated:
        return redirect(url_for("citizen.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f"Welcome back, {user.full_name}!", "success")
            # Admins land on their dashboard (exists from Milestone 4).
            home = url_for("admin.dashboard") if user.is_admin else url_for("citizen.dashboard")
            # Honour Flask-Login's ?next= but never redirect off-site.
            next_page = request.args.get("next")
            if next_page and next_page.startswith("/"):
                return redirect(next_page)
            return redirect(home)
        flash("Invalid e-mail or password.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    """End the current session."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))