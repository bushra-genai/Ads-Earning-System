from . import db
from datetime import datetime

class Withdrawal(db.Model):
    __tablename__ = 'withdrawals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount_usd = db.Column(db.Float, nullable=False)
    amount_pkr = db.Column(db.Float, nullable=False)
    fee = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum('queued', 'approved', 'paid', 'rejected', name='withdrawal_status'), default='queued')
    queue_position = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)