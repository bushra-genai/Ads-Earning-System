from . import db

class ReferralTree(db.Model):
    __tablename__ = 'referral_trees'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    level = db.Column(db.Integer, nullable=False)