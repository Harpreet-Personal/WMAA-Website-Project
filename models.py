from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    VALID_ROLES = {"donor", "volunteer", "admin"}

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    availability = db.Column(db.String(255), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)

    payments = db.relationship("Payment", backref="user", lazy=True, cascade="all, delete-orphan")

    @validates("role")
    def validate_role(self, key, value):
        if value not in self.VALID_ROLES:
            raise ValueError("Role must be donor, volunteer, or admin")
        return value

    def __repr__(self):
        return f"<User {self.email}>"


class Payment(db.Model):
    __tablename__ = "payments"

    VALID_STATUSES = {"pending", "completed", "failed", "refunded"}
    VALID_METHODS = {"card", "bank_transfer", "cash", "paypal", "stripe"}

    payment_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_status = db.Column(db.String(20), nullable=False)
    payment_method = db.Column(db.String(30), nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
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