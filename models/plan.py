from . import db
from datetime import datetime

class Plan(db.Model):
    __tablename__ = 'plans'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # Display name: Basic, Standard, Premium
    slug = db.Column(db.String(50), unique=True, nullable=False)  # API key: basic, standard, premium
    price_usd = db.Column(db.Float, nullable=False)
    price_pkr = db.Column(db.Float, nullable=False)
    ads_limit = db.Column(db.Integer, default=1)
    earning_per_ad = db.Column(db.Float, default=0.10)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'price_usd': self.price_usd,
            'price_pkr': self.price_pkr,
            'ads_limit': self.ads_limit,
            'earning_per_ad': self.earning_per_ad,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
