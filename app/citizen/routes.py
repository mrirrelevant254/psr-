"""Citizen routes: dashboard, submit request, request detail, uploads."""
from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, send_from_directory, url_for)
from flask_login import current_user, login_required

from app.citizen.forms import RequestForm
from app.extensions import db
from app.models import RequestStatus, ServiceRequest, StatusHistory
from app.utils import flash_form_errors, save_image

citizen_bp = Blueprint("citizen", __name__)


@citizen_bp.route("/")
@login_required
def dashboard():
    """List the logged-in citizen's own requests, newest first."""
    requests = (
        ServiceRequest.query
        .filter_by(citizen_id=current_user.id)
        .order_by(ServiceRequest.created_at.desc())
        .all()
    )
    return render_template("citizen/dashboard.html", requests=requests)


@citizen_bp.route("/requests/new", methods=["GET", "POST"])
@login_required
def new_request():
    """Submit a new service request (photo optional)."""
    form = RequestForm()
    if form.validate_on_submit():
        req = ServiceRequest(
            citizen_id=current_user.id,
            category=form.category.data,
            location=form.location.data.strip(),
            description=form.description.data.strip(),
            image_filename=save_image(form.image.data),
            status=RequestStatus.PENDING,
        )
        db.session.add(req)
        db.session.flush()                      # assigns req.id for the history row
        db.session.add(StatusHistory(
            request=req, new_status=RequestStatus.PENDING,
            changed_by=current_user, note="Request submitted",
        ))
        db.session.commit()
        flash(f"Request #{req.id} submitted — track it from your dashboard.", "success")
        return redirect(url_for("citizen.request_detail", request_id=req.id))

    flash_form_errors(form)
    return render_template("citizen/request_form.html", form=form)


@citizen_bp.route("/requests/<int:request_id>")
@login_required
def request_detail(request_id: int):
    """Show one request + its status timeline (owner or admin only)."""
    req = db.session.get(ServiceRequest, request_id)
    if req is None:
        abort(404)
    if req.citizen_id != current_user.id and not current_user.is_admin:
        abort(403)                              # never expose other citizens' cases
    return render_template("citizen/request_detail.html", req=req)


@citizen_bp.route("/uploads/<path:filename>")
@login_required
def uploaded_file(filename: str):
    """Serve an uploaded photo (logged-in users only)."""
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)