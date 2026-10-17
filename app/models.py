"""Database models + workflow constants (single source of truth)."""
from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


# ---------------------------------------------------------------- constants
class UserRole:
    """Possible values for User.role."""
    CITIZEN = "citizen"
    ADMIN = "admin"


class RequestStatus:
    """Status workflow: Pending -> In Progress -> Resolved."""
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    ORDER = (PENDING, IN_PROGRESS, RESOLVED)
    OPEN_STATUSES = (PENDING, IN_PROGRESS)        # used by analytics


class RequestCategory:
    """Pre-defined categories shown in the submit form."""
    STREETLIGHT = "Broken Streetlight"
    WATER = "Water Issue"
    GARBAGE = "Garbage Collection"
    ROADS = "Road / Pavement"
    OTHER = "Other"
    ALL = (STREETLIGHT, WATER, GARBAGE, ROADS, OTHER)


def utcnow() -> datetime:
    """Timezone-aware 'now' used as the default for every timestamp."""
    return datetime.now(timezone.utc)


# ------------------------------------------------------------------- models
class User(UserMixin, db.Model):
    """A registered citizen or administrator."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(10), nullable=False, default=UserRole.CITIZEN)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    requests = db.relationship(
        "ServiceRequest", back_populates="citizen",
        cascade="all, delete-orphan",
    )

    def set_password(self, password: str) -> None:
        """Store a hashed (never plain-text) password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a candidate password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"


class ServiceRequest(db.Model):
    """One public-service issue reported by a citizen."""

    __tablename__ = "service_requests"

    id = db.Column(db.Integer, primary_key=True)
    citizen_id = db.Column(db.Integer, db.ForeignKey("users.id"),
                           nullable=False, index=True)
    category = db.Column(db.String(40), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(255))            # optional photo
    status = db.Column(db.String(20), nullable=False,
                       default=RequestStatus.PENDING, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=utcnow, onupdate=utcnow)

    citizen = db.relationship("User", back_populates="requests")
    history = db.relationship(
        "StatusHistory", back_populates="request",
        cascade="all, delete-orphan",
        order_by="StatusHistory.created_at",
    )

    @property
    def is_open(self) -> bool:
        """True while the case is unresolved (analytics uses this)."""
        return self.status in RequestStatus.OPEN_STATUSES

    @property
    def next_status(self):
        """Next workflow step, or None when already Resolved."""
        idx = RequestStatus.ORDER.index(self.status)
        return RequestStatus.ORDER[idx + 1] if idx + 1 < len(RequestStatus.ORDER) else None

    def update_status(self, new_status: str, changed_by: "User", note: str = "") -> None:
        """Move to *new_status* and record the change in the audit trail."""
        old = self.status
        self.status = new_status
        db.session.add(StatusHistory(
            request=self, old_status=old, new_status=new_status,
            note=note, changed_by=changed_by,
        ))

    def __repr__(self) -> str:
        return f"<ServiceRequest #{self.id} [{self.status}]>"


class StatusHistory(db.Model):
    """Audit trail of status changes (powers the timeline UI - bonus)."""

    __tablename__ = "status_history"

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("service_requests.id"),
                           nullable=False)
    old_status = db.Column(db.String(20))
    new_status = db.Column(db.String(20), nullable=False)
    note = db.Column(db.String(255))
    changed_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    request = db.relationship("ServiceRequest", back_populates="history")
    changed_by = db.relationship("User")