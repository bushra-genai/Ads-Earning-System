from . import db

class Wallet(db.Model):
    __tablename__ = 'wallets'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True, nullable=False)
    balance = db.Column(db.Float, default=0.0)
    withdrawable = db.Column(db.Float, default=0.0)
    total_earned = db.Column(db.Float, default=0.0)