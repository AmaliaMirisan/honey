from datetime import datetime
import json
from sqlalchemy import JSON

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
    honey_words = db.Column(JSON)
    date_created = db.Column(
        db.DateTime(timezone=True), default=func.now()
    )
    honey_word_breached = db.Column(db.Boolean, default=False)
    breached_word = db.Column(db.String(150))
    account = db.relationship('Account', backref='user', lazy=True, foreign_keys='Account.user_id')

    def set_honey_words(self, word_list):
        self.honey_words = json.dumps(word_list)

    @property
    def honey_words_as_list(self):
        return json.loads(self.honey_words)

    @honey_words_as_list.setter
    def honey_words_as_list(self, value):
        self.honey_words = json.dumps(value)

    def honey_words_contains(self, word):
        print(self.honey_words)
        return word in self.honey_words

    def set_honey_word_breached(self, breached):
        self.honey_word_breached = breached
    def set_breached_word(self, word):
        self.breached_word = word



class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id_from = db.Column(db.Integer, db.ForeignKey('account.id'))
    account_id_to = db.Column(db.Integer, db.ForeignKey('account.id'))
    amount = db.Column(db.Float)
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())

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
    balance = db.Column(db.Float)
    currency = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    account_number = db.Column(db.String(150))
    outgoing_transactions = db.relationship(
        "Transactions",
        foreign_keys="Transactions.account_id_from",
        back_populates="from_account"
    )
    incoming_transactions = db.relationship(
        "Transactions",
        foreign_keys="Transactions.account_id_to",
        back_populates="to_account"
    )
