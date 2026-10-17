"""Database models + workflow constants (single source of truth)."""
from datetime import datetime, timedelta

from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class RequestCategory:
    """The service categories a citizen can request."""
    STREETLIGHT = "Streetlight"
    WATER = "Water"
    GARBAGE = "Garbage"
    ROADS = "Roads"
    DRAINAGE = "Drainage"
    OTHER = "Other"
    ALL = (STREETLIGHT, WATER, GARBAGE, ROADS, DRAINAGE, OTHER)


class SubCounty:
    """The 7 sub-counties of Murang'a County."""
    KANDARA = "Kandara"
    KANGEMA = "Kangema"
    KIHARU = "Kiharu"
    MARAGWA = "Maragwa"
    MATHIOYA = "Mathioya"
    GATANGA = "Gatanga"
    MURANGA = "Murang'a"
    ALL = (KANDARA, KANGEMA, KIHARU, MARAGWA, MATHIOYA, GATANGA, MURANGA)


class RequestStatus:
    """The workflow a request moves through."""
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    ORDER = (PENDING, IN_PROGRESS, RESOLVED)

    SLA_DAYS = 7  # Feature 3: requests open longer than this are "Overdue"


class User(db.Model):
    """A registered citizen or administrator."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    requests = db.relationship(
        "ServiceRequest", back_populates="citizen", cascade="all, delete-orphan"
    )
    notifications = db.relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        """Hash and store the password."""
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a plain-text password against the stored hash."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User {self.email} (admin={self.is_admin})>"


class ServiceRequest(db.Model):
    """One public-service issue reported by a citizen."""
    __tablename__ = "service_requests"

    id = db.Column(db.Integer, primary_key=True)
    citizen_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    category = db.Column(db.String(40), nullable=False)
    sub_county = db.Column(db.String(20), nullable=False, index=True)
    location = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False, default=RequestStatus.PENDING)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    citizen = db.relationship("User", back_populates="requests")
    status_history = db.relationship(
        "StatusChange", back_populates="request", cascade="all, delete-orphan"
    )

    @property
    def is_overdue(self):
        """True when the request is still open and older than the SLA."""
        open_statuses = (RequestStatus.PENDING, RequestStatus.IN_PROGRESS)
        if self.status not in open_statuses:
            return False
        return datetime.utcnow() > self.created_at + timedelta(
            days=RequestStatus.SLA_DAYS
        )

    @property
    def next_status(self):
        """Get the next valid status in the workflow (Pending -> In Progress -> Resolved)."""
        try:
            current_index = RequestStatus.ORDER.index(self.status)
            if current_index + 1 < len(RequestStatus.ORDER):
                return RequestStatus.ORDER[current_index + 1]
        except ValueError:
            pass
        return None

    def __repr__(self):
        return f"<ServiceRequest #{self.id} [{self.status}]>"


class StatusChange(db.Model):
    """Audit trail: every status change is recorded."""
    __tablename__ = "status_changes"

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(
        db.Integer, db.ForeignKey("service_requests.id"), nullable=False, index=True
    )
    old_status = db.Column(db.String(20), nullable=True)
    new_status = db.Column(db.String(20), nullable=False)
    changed_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    changed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    request = db.relationship("ServiceRequest", back_populates="status_history")
    changed_by = db.relationship("User")


class Notification(db.Model):
    """Feature 1: in-app notifications for citizens."""
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    message = db.Column(db.String(300), nullable=False)
    read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", back_populates="notifications")