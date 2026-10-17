from functools import wraps

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, send_from_directory, session, url_for)

from app import db
from app.citizen.forms import LoginForm, RegisterForm, RequestForm
from app.models import Notification, RequestStatus, ServiceRequest, User
from app.utils import save_image

citizen_bp = Blueprint("citizen", __name__)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session or session.get("is_admin"):
            flash("Please login as a citizen to continue.", "warning")
            return redirect(url_for("citizen.login"))
        return view(*args, **kwargs)

    return wrapped


def current_user():
    if "user_id" not in session:
        return None
    return db.session.get(User, session["user_id"])


@citizen_bp.route("/")
def index():
    if "user_id" in session:
        if session.get("is_admin"):
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("citizen.dashboard"))
    return redirect(url_for("citizen.login"))


@citizen_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        exists = User.query.filter_by(email=form.email.data.strip()).first()
        if exists:
            flash("That email is already registered.", "danger")
            return render_template("citizen/register.html", form=form)

        user = User(
            email=form.email.data.strip(),
            full_name=form.full_name.data.strip(),
            password=form.password.data,  # demo only: hash in production
        )
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for("citizen.login"))
    return render_template("citizen/register.html", form=form)


@citizen_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip()).first()
        if user and user.password == form.password.data:
            if user.is_admin:
                # Admins have a separate portal. We guide them there only
                # when they prove admin credentials - the link is never
                # advertised on public citizen pages.
                flash("Administrators log in through the county admin portal.", "info")
                return redirect(url_for("admin.login"))
            session.clear()
            session["user_id"] = user.id
            session["is_admin"] = False
            flash(f"Welcome back, {user.full_name}!", "success")
            return redirect(url_for("citizen.dashboard"))
        flash("Invalid citizen credentials.", "danger")
    return render_template("citizen/login.html", form=form)


@citizen_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("citizen.login"))


@citizen_bp.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    requests = (
        ServiceRequest.query.filter_by(citizen_id=user.id)
        .order_by(ServiceRequest.created_at.desc())
        .all()
    )
    notifications = (
        Notification.query.filter_by(user_id=user.id)
        .order_by(Notification.created_at.desc())
        .limit(10)
        .all()
    )
    unread = sum(1 for n in notifications if not n.read)
    return render_template(
        "citizen/dashboard.html",
        user=user, requests=requests,
        notifications=notifications, unread=unread,
    )


@citizen_bp.route("/requests/new", methods=["GET", "POST"])
@login_required
def new_request():
    form = RequestForm()
    if form.validate_on_submit():
        user = current_user()
        req = ServiceRequest(
            citizen_id=user.id,
            category=form.category.data,
            sub_county=form.sub_county.data,
            location=form.location.data.strip(),
            description=form.description.data.strip(),
            image_filename=save_image(form.image.data),   # optional photo
        )
        db.session.add(req)
        db.session.commit()

        db.session.add(Notification(
            user_id=user.id,
            message=f"Request #{req.id} ({req.category}) was received and is Pending.",
        ))
        db.session.commit()

        flash("Your request has been submitted.", "success")
        return redirect(url_for("citizen.dashboard"))
    return render_template("citizen/new_request.html", form=form)


@citizen_bp.route("/requests/<int:request_id>")
@login_required
def request_detail(request_id):
    user = current_user()
    req = ServiceRequest.query.filter_by(id=request_id, citizen_id=user.id).first()
    if req is None:
        flash("Request not found.", "danger")
        return redirect(url_for("citizen.dashboard"))
    return render_template("citizen/request_detail.html", req=req)


@citizen_bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    """Serve an uploaded photo to any logged-in user (citizen or admin)."""
    if "user_id" not in session:
        flash("Please login to view attachments.", "warning")
        return redirect(url_for("citizen.login"))
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


@citizen_bp.route("/notifications/read", methods=["POST"])
@login_required
def mark_notifications_read():
    user = current_user()
    Notification.query.filter_by(user_id=user.id, read=False).update({"read": True})
    db.session.commit()
    return redirect(url_for("citizen.dashboard"))