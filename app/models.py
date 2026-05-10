from .extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    income_range = db.Column(db.String(50), nullable=True)
    spending_habit = db.Column(db.String(50), nullable=True)
    profile_photo = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    goals = db.relationship('SavingsGoal', backref='user', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    coach_messages = db.relationship('CoachMessage', backref='user', lazy=True)


class SavingsGoal(db.Model):
    __tablename__ = 'savings_goals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    deadline = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='active')  # active, completed, paused
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    virtual_account = db.relationship('VirtualAccount', backref='goal', uselist=False, lazy=True)
    transactions = db.relationship('Transaction', backref='goal', lazy=True)


class VirtualAccount(db.Model):
    __tablename__ = 'virtual_accounts'

    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('savings_goals.id'), nullable=False)
    squad_account_ref = db.Column(db.String(100), unique=True, nullable=False)
    account_number = db.Column(db.String(20), nullable=False)
    bank_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    goal_id = db.Column(db.Integer, db.ForeignKey('savings_goals.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    squad_ref = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed
    paid_at = db.Column(db.DateTime, default=datetime.utcnow)


class CoachMessage(db.Model):
    __tablename__ = 'coach_messages'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # user, assistant
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)