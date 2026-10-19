"""Admin routes: login, dashboard, request queue, status updates, and CSV export."""
import csv
import io
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Blueprint, Response, flash, redirect, render_template, request, session,
    url_for,
)
from sqlalchemy import func

from app import db
from app.citizen.forms import LoginForm
from app.models import (
    Notification, RequestCategory, RequestStatus, ServiceRequest, StatusChange,
    SubCounty, User,
)

admin_bp = Blueprint("admin", __name__)


def admin_required(view):
    """Decorator to ensure only logged-in administrators can access a route."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Please login as an administrator.", "warning")
            return redirect(url_for("admin.login"))
        return view(*args, **kwargs)
    return wrapped


def current_admin():
    """Helper to get the current logged-in admin object."""
    if not session.get("is_admin"):
        return None
    return db.session.get(User, session["user_id"])


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle administrator login."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and user.check_password(form.password.data) and user.is_admin:
            session.clear()
            session["user_id"] = user.id
            session["is_admin"] = True
            flash("Administrator login successful.", "success")
            return redirect(url_for("admin.dashboard"))
        flash("Invalid administrator credentials.", "danger")
    return render_template("admin/login.html", form=form)


@admin_bp.route("/logout")
def logout():
    """Clear session and log out the administrator."""
    session.clear()
    flash("Administrator logged out.", "info")
    return redirect(url_for("admin.login"))


@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    """Admin analytics dashboard with custom progress bars."""
    total = ServiceRequest.query.count()
    
    open_count = ServiceRequest.query.filter(
        ServiceRequest.status.in_([RequestStatus.PENDING, RequestStatus.IN_PROGRESS])
    ).count()
    
    resolved = ServiceRequest.query.filter_by(status=RequestStatus.RESOLVED).count()

    # Specific counts for the stacked "Open vs resolved" progress bar
    pending = ServiceRequest.query.filter_by(status=RequestStatus.PENDING).count()
    in_progress = ServiceRequest.query.filter_by(status=RequestStatus.IN_PROGRESS).count()

    # SLA Overdue calculation
    cutoff = datetime.utcnow() - timedelta(days=RequestStatus.SLA_DAYS)
    overdue = ServiceRequest.query.filter(
        ServiceRequest.status.in_([RequestStatus.PENDING, RequestStatus.IN_PROGRESS]),
        ServiceRequest.created_at < cutoff,
    ).count()

    # Chart data (kept for fallback, though HTML now uses custom bars)
    status_chart = dict(
        db.session.query(ServiceRequest.status, func.count(ServiceRequest.id))
        .group_by(ServiceRequest.status).all()
    )
    category_counts = dict(
        db.session.query(ServiceRequest.category, func.count(ServiceRequest.id))
        .group_by(ServiceRequest.category).all()
    )
    ward_counts = dict(
        db.session.query(ServiceRequest.sub_county, func.count(ServiceRequest.id))
        .group_by(ServiceRequest.sub_county).all()
    )

    stats = {
        "total": total, 
        "open": open_count, 
        "resolved": resolved, 
        "overdue": overdue,
        "pending": pending,       # Added for progress bar
        "in_progress": in_progress # Added for progress bar
    }
    
    return render_template(
        "admin/dashboard.html",
        stats=stats, status_chart=status_chart,
        category_counts=category_counts, ward_counts=ward_counts,
    )


def build_queue_query():
    """Apply status/category/sub-county/search filters from the query string."""
    query = ServiceRequest.query
    status = request.args.get("status", "")
    category = request.args.get("category", "")
    sub_county = request.args.get("sub_county", "")
    search = request.args.get("q", "").strip()

    if status in RequestStatus.ORDER:
        query = query.filter_by(status=status)
    if category in RequestCategory.ALL:
        query = query.filter_by(category=category)
    if sub_county in SubCounty.ALL:
        query = query.filter_by(sub_county=sub_county)
    if search:
        like = f"%{search}%"
        query = query.filter(db.or_(
            ServiceRequest.location.ilike(like),
            ServiceRequest.description.ilike(like),
            ServiceRequest.citizen.has(User.email.ilike(like)),
        ))
    return query, status, category, sub_county, search


@admin_bp.route("/requests")
@admin_required
def requests():
    """View the filtered request queue."""
    query, status, category, sub_county, search = build_queue_query()
    items = query.order_by(ServiceRequest.created_at.desc()).all()
    return render_template(
        "admin/requests.html",
        requests=items, status=status, category=category,
        sub_county=sub_county, search=search,
        statuses=RequestStatus.ORDER, categories=RequestCategory.ALL,
        sub_counties=SubCounty.ALL,
    )


@admin_bp.route("/requests/export.csv")
@admin_required
def export_csv():
    """Export the current filtered queue to a CSV file."""
    query, _status, _category, _sub_county, _search = build_queue_query()
    items = query.order_by(ServiceRequest.created_at.desc()).all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["ID", "Citizen", "Email", "Category", "Sub-County", "Location",
                     "Description", "Status", "Created", "Updated"])
    for r in items:
        writer.writerow([
            r.id, r.citizen.full_name, r.citizen.email, r.category, r.sub_county,
            r.location, r.description, r.status,
            r.created_at.strftime("%Y-%m-%d %H:%M"),
            r.updated_at.strftime("%Y-%m-%d %H:%M"),
        ])
    return Response(
        buffer.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=requests.csv"},
    )


@admin_bp.route("/requests/<int:request_id>")
@admin_required
def request_detail(request_id):
    """View a specific request and its audit trail."""
    req = db.session.get(ServiceRequest, request_id)
    if req is None:
        flash("Request not found.", "danger")
        return redirect(url_for("admin.requests"))
    return render_template(
        "admin/request_detail.html", req=req, statuses=RequestStatus.ORDER
    )


@admin_bp.route("/requests/<int:request_id>/status", methods=["POST"])
@admin_required
def update_status(request_id):
    """Update the status of a request (enforces one-way workflow)."""
    req = db.session.get(ServiceRequest, request_id)
    if req is None:
        flash("Request not found.", "danger")
        return redirect(url_for("admin.requests"))

    new_status = request.form.get("status", "")
    
    # Security check: ensure the requested status is the actual next step
    if new_status != req.next_status:
        flash("Invalid status transition.", "danger")
        return redirect(url_for("admin.request_detail", request_id=req.id))

    admin = current_admin()
    old_status = req.status
    req.status = new_status
    
    db.session.add(StatusChange(
        request_id=req.id, old_status=old_status,
        new_status=new_status, changed_by_id=admin.id,
    ))
    
    # Notify the citizen
    db.session.add(Notification(
        user_id=req.citizen_id,
        message=f"Request #{req.id} ({req.category}) moved from {old_status} to {new_status}.",
    ))
    db.session.commit()

    flash(f"Status updated to {new_status}.", "success")
    return redirect(url_for("admin.request_detail", request_id=req.id))