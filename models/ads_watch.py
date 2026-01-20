from . import db
from datetime import date

class AdsWatch(db.Model):
    __tablename__ = 'ads_watches'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True, nullable=False)
    date = db.Column(db.Date, primary_key=True, nullable=False)
    watched = db.Column(db.Boolean, default=False)
    earned_amount = db.Column(db.Float, default=0.0)