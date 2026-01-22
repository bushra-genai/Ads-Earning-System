from app import app
from models import db, Deposit, AdsWatch

def check_user_history(user_id):
    with app.app_context():
        deposits = Deposit.query.filter_by(user_id=user_id).all()
        print(f"Deposits for user {user_id}:")
        for d in deposits:
            print(f" - ID: {d.id}, Amount: {d.amount}, Status: {d.status}")
        
        ads = AdsWatch.query.filter_by(user_id=user_id).all()
        print(f"\nAds Watches for user {user_id}: {len(ads)}")
        total_ad_earnings = sum(a.earned_amount for a in ads if a.watched)
        print(f"Total Ad Earnings: {total_ad_earnings}")

if __name__ == "__main__":
    check_user_history(1)
