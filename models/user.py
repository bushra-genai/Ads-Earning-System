from . import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    referral_code = db.Column(db.String(50), unique=True, nullable=True)
    referred_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    plan_active = db.Column(db.Boolean, default=False)
    role = db.Column(db.Enum('admin', 'user', name='user_role'), default='user')
    status = db.Column(db.Enum('active', 'suspended', 'banned', name='user_status'), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, nullable=True)

    # Relationships
    wallet = db.relationship('Wallet', backref='user', uselist=False)
    deposits = db.relationship('Deposit', backref='user', lazy=True)
    withdrawals = db.relationship('Withdrawal', backref='user', lazy=True)
    ads_watches = db.relationship('AdsWatch', backref='user', lazy=True)
    referrals = db.relationship('ReferralTree', backref='user', lazy=True, foreign_keys='ReferralTree.user_id')