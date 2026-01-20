from . import db
from datetime import datetime

class RankRewards(db.Model):
    __tablename__ = 'rank_rewards'

    id = db.Column(db.Integer, primary_key=True)
    leader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    member_deposit = db.Column(db.Float, nullable=False)
    reward_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)