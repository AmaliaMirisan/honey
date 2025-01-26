from datetime import datetime

from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    # Establish one-to-one relationship with Account
    account = db.relationship('Account', back_populates='user', uselist=False)
class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    balance = db.Column(db.Float, nullable=False, default=0.0)
    currency = db.Column(db.String(10), nullable=False, default='USD')
    account_number = db.Column(db.String(20), unique=True, nullable=False)

    # Establish one-to-one relationship with User
    user = db.relationship('User', back_populates='account')


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id_from = db.Column(db.Integer, nullable=False)
    account_id_to = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)



