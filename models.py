import re
import json
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import func
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    VALID_ROLES = {"donor", "volunteer", "admin"}

    id            = db.Column(db.Integer, primary_key=True)
    full_name     = db.Column(db.String(150), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    phone_number  = db.Column(db.String(20),  nullable=False)
    role          = db.Column(db.String(20),  nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at    = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    last_login    = db.Column(db.DateTime, nullable=True)
    availability  = db.Column(db.String(255), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    is_active     = db.Column(db.Boolean, default=True, nullable=False)

    payments = db.relationship("Payment", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
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
    Payment model — kept exactly as the original working version.
    NO user_name / user_email columns.
    Donor name/email is retrieved at runtime via the 'user' relationship backref.
    """
    __tablename__ = "payments"

    VALID_STATUSES = {"pending", "completed", "failed", "refunded"}
    VALID_METHODS  = {"card", "bank_transfer", "cash", "paypal", "stripe"}

    payment_id        = db.Column(db.Integer, primary_key=True)
    user_id           = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount            = db.Column(db.Numeric(10, 2), nullable=False)
    payment_status    = db.Column(db.String(20), nullable=False)
    payment_method    = db.Column(db.String(30), nullable=False)
    payment_date      = db.Column(db.DateTime, server_default=func.now(), nullable=False)
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


class Event(db.Model):
    __tablename__ = "events"

    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    date        = db.Column(db.String(20),  nullable=True)
    time        = db.Column(db.String(50),  nullable=True)
    location    = db.Column(db.String(200), nullable=True)
    category    = db.Column(db.String(50),  nullable=True)
    event_type  = db.Column(db.String(20),  nullable=False)
    description = db.Column(db.Text,        nullable=True)
    image_url   = db.Column(db.String(300), nullable=True)
    created_at  = db.Column(db.DateTime, server_default=func.now(), nullable=False)

    def to_dict(self):
        """Plain dict with only JSON-safe types — used by tojson filter in templates."""
        return {
            "id":          self.id,
            "title":       self.title       or "",
            "date":        self.date        or "",
            "time":        self.time        or "",
            "location":    self.location    or "",
            "category":    self.category    or "",
            "event_type":  self.event_type  or "",
            "description": self.description or "",
            "image_url":   self.image_url   or "",
        }

    def __repr__(self):
        return f"<Event {self.id}: {self.title}>"


class NewsArticle(db.Model):
    __tablename__ = "news_articles"

    id           = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.String(200), nullable=False)
    category     = db.Column(db.String(50),  nullable=False)
    date         = db.Column(db.String(20),  nullable=True)
    excerpt      = db.Column(db.String(300), nullable=True)
    full_content = db.Column(db.Text,        nullable=True)
    image_url    = db.Column(db.String(300), nullable=True)
    created_at   = db.Column(db.DateTime, server_default=func.now(), nullable=False)

    def to_dict(self):
        return {
            "id":           self.id,
            "title":        self.title        or "",
            "category":     self.category     or "",
            "date":         self.date         or "",
            "excerpt":      self.excerpt      or "",
            "full_content": self.full_content or "",
            "image_url":    self.image_url    or "",
        }

    def __repr__(self):
        return f"<NewsArticle {self.id}: {self.title}>"


class Story(db.Model):
    __tablename__ = "stories"

    id         = db.Column(db.Integer, primary_key=True)
    title      = db.Column(db.String(200), nullable=False)
    category   = db.Column(db.String(100), nullable=False)
    content    = db.Column(db.Text,        nullable=False)
    image_url  = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)

    def to_dict(self):
        return {
            "id":        self.id,
            "title":     self.title    or "",
            "category":  self.category or "",
            "content":   self.content  or "",
            "image_url": self.image_url or "",
        }

    def __repr__(self):
        return f"<Story {self.id}: {self.title}>"


class Service(db.Model):
    __tablename__ = "services"

    id                = db.Column(db.Integer, primary_key=True)
    slug              = db.Column(db.String(50),  unique=True, nullable=False)
    icon              = db.Column(db.String(50),  nullable=True)
    title             = db.Column(db.String(200), nullable=False)
    label             = db.Column(db.String(200), nullable=True)
    short_description = db.Column(db.Text, nullable=True)
    long_description  = db.Column(db.Text, nullable=True)
    _detail_items     = db.Column("detail_items", db.Text, nullable=True)

    @property
    def detail_items(self):
        try:
            return json.loads(self._detail_items) if self._detail_items else []
        except Exception:
            return []

    @detail_items.setter
    def detail_items(self, value):
        self._detail_items = json.dumps(value or [])

    def __repr__(self):
        return f"<Service {self.slug}>"


class HomeContent(db.Model):
    """Single-row table (always id=1). Stores all editable home page content."""
    __tablename__ = "home_content"

    id                      = db.Column(db.Integer, primary_key=True)
    hero_heading            = db.Column(db.Text,        nullable=True)
    hero_sub                = db.Column(db.Text,        nullable=True)
    hero_btn_primary_text   = db.Column(db.String(100), nullable=True)
    hero_btn_secondary_text = db.Column(db.String(100), nullable=True)
    hero_image_url          = db.Column(db.String(300), nullable=True)
    about_heading           = db.Column(db.String(200), nullable=True)
    about_body              = db.Column(db.Text,        nullable=True)
    about_image_url         = db.Column(db.String(300), nullable=True)
    vision_text             = db.Column(db.Text,        nullable=True)
    donate_strip_heading    = db.Column(db.String(200), nullable=True)
    donate_strip_body       = db.Column(db.Text,        nullable=True)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return "<HomeContent>"