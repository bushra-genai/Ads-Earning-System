from . import db
from datetime import datetime

class Deposit(db.Model):
    __tablename__ = 'deposits'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    screenshot_url = db.Column(db.String(255), nullable=True)
    deposit_type = db.Column(db.Enum('regular', 'plan_purchase', name='deposit_type'), default='regular')
    plan_name = db.Column(db.String(50), nullable=True)
    status = db.Column(db.Enum('pending', 'approved', 'rejected', name='deposit_status'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)