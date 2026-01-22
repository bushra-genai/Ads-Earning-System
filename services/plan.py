import logging
from models import db, User, Deposit, Plan
from config import LOG_FILE, LOG_LEVEL

logging.basicConfig(filename=LOG_FILE, level=getattr(logging, LOG_LEVEL), format='%(asctime)s - %(levelname)s - %(message)s')

def get_plan_from_db(plan_slug):
    """
    Get plan from database by slug.
    """
    return Plan.query.filter_by(slug=plan_slug, is_active=True).first()

def purchase_plan(user_id, plan_slug, screenshot_url):
    """
    User selects a plan, creating a pending plan_purchase deposit.
    """
    try:
        plan = get_plan_from_db(plan_slug)
        if not plan:
            raise ValueError(f"Invalid plan selected: {plan_slug}")

        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        if user.plan_status == 'active':
            raise ValueError("User already has an active plan")

        # Create a special deposit for plan purchase
        deposit = Deposit(
            user_id=user_id,
            amount=plan.price_usd,
            screenshot_url=screenshot_url,
            deposit_type='plan_purchase',
            plan_name=plan_slug,
            status='pending'
        )
        
        user.plan_status = 'pending'
        user.active_plan = plan_slug
        
        db.session.add(deposit)
        db.session.commit()
        
        logging.info(f"User {user_id} initiated purchase for plan {plan_slug}")
        return deposit
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error initiating plan purchase for user {user_id}: {str(e)}")
        raise

def activate_user_plan(user_id, plan_slug):
    """
    Activate user's plan and set permissions/limits.
    """
    try:
        plan = get_plan_from_db(plan_slug)
        if not plan:
            raise ValueError(f"Invalid plan to activate: {plan_slug}")

        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        user.plan_status = 'active'
        user.active_plan = plan_slug
        user.ads_permission = True
        user.daily_ads_limit = plan.ads_limit
        
        db.session.commit()
        logging.info(f"Plan {plan_slug} activated for user {user_id}")
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error activating plan {plan_slug} for user {user_id}: {str(e)}")
        raise

