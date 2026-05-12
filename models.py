import re
from flask_sqlalchemy import SQLAlchemy

# UserMixin provides default implementations required by Flask-Login
# (is_authenticated, is_active, is_anonymous, get_id)
from flask_login import UserMixin

from sqlalchemy import func
from sqlalchemy.orm import validates

# Werkzeug utilities for securely hashing and verifying passwords
from werkzeug.security import generate_password_hash, check_password_hash

# Shared SQLAlchemy instance — initialised in app.py via db.init_app(app)
db = SQLAlchemy()


class User(UserMixin, db.Model):
    """
    User model representing all registered accounts.
    Roles: 'volunteer', 'donor', 'admin'
    Password is never stored in plain text — only the hash is saved.
    """
    __tablename__ = "users"

    VALID_ROLES = {"donor", "volunteer", "admin"}

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)

    # Tracks when the user last logged in — updated on each successful login
    last_login = db.Column(db.DateTime, nullable=True)

    # Stores volunteer's selected area of interest from the signup form
    availability = db.Column(db.String(255), nullable=True)

    date_of_birth = db.Column(db.Date, nullable=True)

    # Soft-delete flag — set to False to deactivate without deleting the record
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # One user can have many payments; deleting a user cascades to their payments
    payments = db.relationship("Payment", backref="user", lazy=True, cascade="all, delete-orphan")

    volunteer_profile = db.relationship(
        "VolunteerProfile",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    volunteer_schedules = db.relationship(
    "VolunteerSchedule",
    backref="volunteer",
    lazy=True,
    cascade="all, delete-orphan"
    )

    volunteer_hours = db.relationship(
    "VolunteerHours",
    backref="volunteer",
    lazy=True,
    cascade="all, delete-orphan"
    )

    volunteer_availability = db.relationship(
    "VolunteerAvailability",
    backref="volunteer",
    lazy=True,
    cascade="all, delete-orphan"
    )

    volunteer_attendance = db.relationship(
    "VolunteerAttendance",
    backref="volunteer",
    lazy=True,
    cascade="all, delete-orphan"
    )


    def set_password(self, password):
        # Hashes the plain-text password and stores it — called during signup
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # Verifies a plain-text password against the stored hash — called during login
        return check_password_hash(self.password_hash, password)

    @validates("role")
    def validate_role(self, key, value):
        if value not in self.VALID_ROLES:
            raise ValueError("Role must be donor, volunteer, or admin")
        return value

    @validates("phone_number")
    def validate_phone(self, key, value):
        if not re.match(r"^\+?[\d\s-]{7,20}$", value):
            raise ValueError("Invalid phone number format")
        return value

    def __repr__(self):
        return f"<User {self.email}>"


class Payment(db.Model):
    """
    Payment model for tracking donations and transactions linked to users.
    """
    __tablename__ = "payments"

    VALID_STATUSES = {"pending", "completed", "failed", "refunded"}
    VALID_METHODS = {"card", "bank_transfer", "cash", "paypal", "stripe"}

    payment_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_status = db.Column(db.String(20), nullable=False)
    payment_method = db.Column(db.String(30), nullable=False)
    payment_date = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    invoice_reference = db.Column(db.String(100), unique=True, nullable=True)

    @validates("payment_status")
    def validate_payment_status(self, key, value):
        if value not in self.VALID_STATUSES:
            raise ValueError("Invalid payment status")
        return value

    @validates("payment_method")
    def validate_payment_method(self, key, value):
        if value not in self.VALID_METHODS:
            raise ValueError("Invalid payment method")
        return value

    @validates("amount")
    def validate_amount(self, key, value):
        if value is None or value <= 0:
            raise ValueError("Amount must be greater than 0")
        return value

    def __repr__(self):
        return f"<Payment {self.payment_id} - {self.payment_status}>"

class VolunteerProfile(db.Model):
    """
    Stores volunteer-specific profile information.
    Linked to the User model.
    """

    __tablename__ = "volunteer_profiles"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    full_name = db.Column(db.String(150), nullable=False)

    email = db.Column(db.String(120), nullable=False)

    phone_number = db.Column(db.String(20), nullable=False)

    area_of_interest = db.Column(db.String(100), nullable=True)

    availability = db.Column(db.String(255), nullable=True)

    emergency_contact = db.Column(db.String(150), nullable=True)

    created_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    @validates("phone_number")
    def validate_phone(self, key, value):
        if not re.match(r"^\+?[\d\s-]{7,20}$", value):
            raise ValueError("Invalid phone number format")
        return value

    def __repr__(self):
        return f"<VolunteerProfile {self.full_name}>"
    

class VolunteerSchedule(db.Model):
    """
    Stores volunteer schedules, shifts, and event assignments.
    """

    __tablename__ = "volunteer_schedules"

    id = db.Column(db.Integer, primary_key=True)

    volunteer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    event_name = db.Column(db.String(150), nullable=False)

    event_date = db.Column(db.Date, nullable=False)

    start_time = db.Column(db.Time, nullable=False)

    end_time = db.Column(db.Time, nullable=False)

    location = db.Column(db.String(255), nullable=True)

    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        nullable=False
    )

    def __repr__(self):
        return f"<VolunteerSchedule {self.event_name}>"

class VolunteerHours(db.Model):
    """
    Tracks volunteer completed hours for dashboard statistics.
    """

    __tablename__ = "volunteer_hours"

    id = db.Column(db.Integer, primary_key=True)

    volunteer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    schedule_id = db.Column(
        db.Integer,
        db.ForeignKey("volunteer_schedules.id", ondelete="CASCADE"),
        nullable=False
    )

    hours_completed = db.Column(db.Float, nullable=False)

    approval_status = db.Column(
        db.String(50),
        nullable=False,
        default="pending"
    )

    submitted_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        nullable=False
    )

    schedule = db.relationship(
        "VolunteerSchedule",
        backref="hour_entries"
    )

    def __repr__(self):
        return f"<VolunteerHours {self.hours_completed} hrs>"

class VolunteerAvailability(db.Model):
    """
    Stores volunteer availability preferences and scheduling slots.
    """

    __tablename__ = "volunteer_availability"

    id = db.Column(db.Integer, primary_key=True)

    volunteer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    available_date = db.Column(db.Date, nullable=False)

    start_time = db.Column(db.Time, nullable=False)

    end_time = db.Column(db.Time, nullable=False)

    estimated_hours = db.Column(db.Float, nullable=True)

    shift_type = db.Column(db.String(100), nullable=True)

    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        nullable=False
    )

    def __repr__(self):
        return f"<VolunteerAvailability {self.available_date}>"

class VolunteerAttendance(db.Model):
    """
    Tracks volunteer attendance for events and scheduled shifts.
    """

    __tablename__ = "volunteer_attendance"

    id = db.Column(db.Integer, primary_key=True)

    volunteer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    schedule_id = db.Column(
        db.Integer,
        db.ForeignKey("volunteer_schedules.id", ondelete="CASCADE"),
        nullable=False
    )

    check_in_time = db.Column(db.DateTime, nullable=True)

    check_out_time = db.Column(db.DateTime, nullable=True)

    attendance_status = db.Column(
        db.String(50),
        nullable=False,
        default="pending"
    )

    created_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        nullable=False
    )

    schedule = db.relationship(
        "VolunteerSchedule",
        backref="attendance_records"
    )

    def __repr__(self):
        return f"<VolunteerAttendance {self.attendance_status}>"