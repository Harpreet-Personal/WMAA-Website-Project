from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id               = db.Column(db.Integer,     primary_key=True)
    first_name       = db.Column(db.String(100), nullable=False)
    last_name        = db.Column(db.String(100), nullable=False)
    email            = db.Column(db.String(150), unique=True, nullable=False)
    password_hash    = db.Column(db.String(256), nullable=False)
    phone            = db.Column(db.String(20),  nullable=True)
    area_of_interest = db.Column(db.String(100), nullable=True)
    languages        = db.Column(db.String(200), nullable=True)
    mfa_pin          = db.Column(db.String(4),   nullable=True)
    mfa_expiry       = db.Column(db.DateTime,    nullable=True)
    is_verified      = db.Column(db.Boolean,     default=False)
    created_at       = db.Column(db.DateTime,    default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.email}>'