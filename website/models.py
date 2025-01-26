from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ARRAY


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
    honey_words = db.Column(ARRAY(db.String(150)))
    date_created = db.Column(
        db.DateTime(timezone=True), default=func.now()
    )
    account = db.relationship('Account', backref='user', lazy=True, foreign_keys='Account.user_id')

    def set_honey_words(self, words):
        if isinstance(words, list) and all(isinstance(word, str) for word in words):
            self.honey_words = words
        else:
            raise ValueError("Honey words must be a list of strings.")

    def get_honey_words(self):
        return self.honey_words

    def in_honey_words(self, text):
        return text in self.honey_words

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id_from = db.Column(db.Integer, db.ForeignKey('account.id'))
    account_id_to = db.Column(db.Integer, db.ForeignKey('account.id'))
    amount = db.Column(db.Float)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    from_account = db.relationship(
        "Account",
        foreign_keys=[account_id_from],
        back_populates="outgoing_transactions"
    )
    to_account = db.relationship(
        "Account",
        foreign_keys=[account_id_to],
        back_populates="incoming_transactions"
    )

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    balance = db.Column(db.Float)
    currency = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    account_number = db.Column(db.String(150))
    outgoing_transactions = db.relationship(
        "Transaction",
        foreign_keys="Transaction.account_id_from",
        back_populates="from_account"
    )

    # Transactions where this account is the receiver
    incoming_transactions = db.relationship(
        "Transaction",
        foreign_keys="Transaction.account_id_to",
        back_populates="to_account"
    )
