import logging
from datetime import date
from models import db, AdsWatch, User
from config import AD_REWARD, LOG_FILE, LOG_LEVEL
from .wallet import update_wallet_balance

logging.basicConfig(filename=LOG_FILE, level=getattr(logging, LOG_LEVEL), format='%(asctime)s - %(levelname)s - %(message)s')

def watch_ad(user_id):
    """
    Handle ad watching logic with daily reset and plan limits.
    """
    try:
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
            
        today = date.today()
        ad_watch = AdsWatch.query.filter_by(user_id=user_id, date=today).first()
        if not ad_watch:
            ad_watch = AdsWatch(user_id=user_id, date=today, ads_watched=0, earned_amount=0.0)
            db.session.add(ad_watch)

        if ad_watch.ads_watched >= user.daily_ads_limit:
            raise ValueError(f"Daily ad limit reached ({user.daily_ads_limit} ads)")

        ad_watch.ads_watched += 1
        ad_watch.earned_amount += AD_REWARD
        
        # Credit both total balance and withdrawable balance
        update_wallet_balance(user_id, AD_REWARD, 'credit')
        from .wallet import update_withdrawable_balance
        update_withdrawable_balance(user_id, AD_REWARD, 'credit')
        logging.info(f"Ad {ad_watch.ads_watched} watched by user {user_id}, earned {AD_REWARD}")
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error watching ad for user {user_id}: {str(e)}")
        raise

def reset_daily_ads():
    """
    Reset daily ad watches. Call this daily.
    """
    try:
        # This could be called by scheduler to reset for all users, but for now, placeholder
        # Perhaps update all AdsWatch for previous days or something, but since date is primary, maybe not needed if we check date.
        # Actually, since we create new for each day, no need to reset.
        pass
    except Exception as e:
        logging.error(f"Error resetting daily ads: {str(e)}")
        raise