"""Admin routes: analytics dashboard, request queue, status workflow."""
from flask import (Blueprint, abort, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required
from sqlalchemy import func

from app.extensions import db
from app.models import (RequestCategory, RequestStatus, ServiceRequest, User)
from app.utils import admin_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    """Analytics overview: open vs resolved + per-category counts."""
    status_counts = dict(
        db.session.query(ServiceRequest.status, func.count(ServiceRequest.id))
        .group_by(ServiceRequest.status).all()
    )
    category_counts = dict(
        db.session.query(ServiceRequest.category, func.count(ServiceRequest.id))
        .group_by(ServiceRequest.category).all()
    )

    total = sum(status_counts.values())
    resolved = status_counts.get(RequestStatus.RESOLVED, 0)
    stats = {
        "total": total,
        "pending": status_counts.get(RequestStatus.PENDING, 0),
        "in_progress": status_counts.get(RequestStatus.IN_PROGRESS, 0),
        "resolved": resolved,
        "open": total - resolved,
    }
    # Fixed key order so doughnut colours always match their labels.
    status_chart = {s: status_counts.get(s, 0) for s in RequestStatus.ORDER}

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        status_chart=status_chart,
        category_counts=category_counts,
    )


@admin_bp.route("/requests")
@login_required
@admin_required
def requests():
    """Every request, with status/category filters and free-text search."""
    query = ServiceRequest.query
    status = request.args.get("status", "")
    category = request.args.get("category", "")
    search = request.args.get("q", "").strip()

    if status in RequestStatus.ORDER:
        query = query.filter_by(status=status)
    if category in RequestCategory.ALL:
        query = query.filter_by(category=category)
    if search:
        like = f"%{search}%"
        query = query.filter(db.or_(
            ServiceRequest.location.ilike(like),
            ServiceRequest.description.ilike(like),
            ServiceRequest.citizen.has(User.email.ilike(like)),
        ))

    items = query.order_by(ServiceRequest.created_at.desc()).all()
    return render_template(
        "admin/requests.html",
        requests=items,
        status=status,
        category=category,
        search=search,
        statuses=RequestStatus.ORDER,
        categories=RequestCategory.ALL,
    )


@admin_bp.route("/requests/<int:request_id>/status", methods=["POST"])
@login_required
@admin_required
def update_status(request_id: int):
    """Advance a request ONE step: Pending -> In Progress -> Resolved.

    The workflow is enforced server-side: `next_status` returns None once
    the request is resolved, so no illegal jumps are possible.
    """
    req = db.session.get(ServiceRequest, request_id)
    if req is None:
        abort(404)

    new_status = req.next_status
    if new_status is None:
        flash("That request is already resolved.", "warning")
    else:
        note = (request.form.get("note") or "").strip()[:255]
        req.update_status(new_status, changed_by=current_user, note=note)
        db.session.commit()
        flash(f"Request #{req.id} moved to '{new_status}'.", "success")

    return redirect(request.referrer or url_for("admin.requests"))