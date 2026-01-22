import logging
from models import db, Plan
from config import LOG_FILE, LOG_LEVEL

logging.basicConfig(filename=LOG_FILE, level=getattr(logging, LOG_LEVEL), format='%(asctime)s - %(levelname)s - %(message)s')

# Default plans configuration
DEFAULT_PLANS = [
    {
        'name': 'Basic',
        'slug': 'basic',
        'price_usd': 3,
        'price_pkr': 840,
        'ads_limit': 1,
        'earning_per_ad': 0.10
    },
    {
        'name': 'Standard',
        'slug': 'standard',
        'price_usd': 7,
        'price_pkr': 1960,
        'ads_limit': 1,
        'earning_per_ad': 0.10
    },
    {
        'name': 'Premium',
        'slug': 'premium',
        'price_usd': 10,
        'price_pkr': 2800,
        'ads_limit': 1,
        'earning_per_ad': 0.10
    }
]


def initialize_default_plans():
    """
    Initialize default plans if none exist in database.
    Call this on app startup.
    """
    try:
        # Check each default plan and create if missing
        count_created = 0
        for plan_data in DEFAULT_PLANS:
            slug = plan_data['slug']
            existing_plan = Plan.query.filter_by(slug=slug).first()
            if not existing_plan:
                plan = Plan(**plan_data)
                db.session.add(plan)
                count_created += 1
        
        if count_created > 0:
            db.session.commit()
            logging.info(f"Initialized {count_created} missing default plans")
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error initializing default plans: {str(e)}")
        raise


def get_all_plans(include_inactive=False):
    """
    Get all plans from database.
    """
    try:
        if include_inactive:
            plans = Plan.query.all()
        else:
            plans = Plan.query.filter_by(is_active=True).all()
        return plans
    except Exception as e:
        logging.error(f"Error fetching plans: {str(e)}")
        raise


def get_plan_by_id(plan_id):
    """
    Get a plan by its ID.
    """
    try:
        plan = Plan.query.get(plan_id)
        return plan
    except Exception as e:
        logging.error(f"Error fetching plan {plan_id}: {str(e)}")
        raise


def get_plan_by_slug(slug):
    """
    Get a plan by its slug.
    """
    try:
        plan = Plan.query.filter_by(slug=slug, is_active=True).first()
        return plan
    except Exception as e:
        logging.error(f"Error fetching plan by slug {slug}: {str(e)}")
        raise


def create_plan(name, slug, price_usd, price_pkr, ads_limit=1, earning_per_ad=0.10):
    """
    Create a new plan.
    """
    try:
        # Check if slug already exists
        existing = Plan.query.filter_by(slug=slug).first()
        if existing:
            raise ValueError(f"Plan with slug '{slug}' already exists")
        
        plan = Plan(
            name=name,
            slug=slug,
            price_usd=price_usd,
            price_pkr=price_pkr,
            ads_limit=ads_limit,
            earning_per_ad=earning_per_ad
        )
        db.session.add(plan)
        db.session.commit()
        logging.info(f"Created new plan: {name} (slug: {slug})")
        return plan
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating plan: {str(e)}")
        raise


def update_plan(plan_id, **kwargs):
    """
    Update an existing plan.
    """
    try:
        plan = Plan.query.get(plan_id)
        if not plan:
            raise ValueError(f"Plan with ID {plan_id} not found")
        
        # Check if updating slug to an existing one
        if 'slug' in kwargs and kwargs['slug'] != plan.slug:
            existing = Plan.query.filter_by(slug=kwargs['slug']).first()
            if existing:
                raise ValueError(f"Plan with slug '{kwargs['slug']}' already exists")
        
        # Update allowed fields
        allowed_fields = ['name', 'slug', 'price_usd', 'price_pkr', 'ads_limit', 'earning_per_ad', 'is_active']
        for field in allowed_fields:
            if field in kwargs:
                setattr(plan, field, kwargs[field])
        
        db.session.commit()
        logging.info(f"Updated plan {plan_id}: {kwargs}")
        return plan
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating plan {plan_id}: {str(e)}")
        raise


def delete_plan(plan_id, hard_delete=False):
    """
    Delete a plan. Soft delete by default.
    """
    try:
        plan = Plan.query.get(plan_id)
        if not plan:
            raise ValueError(f"Plan with ID {plan_id} not found")
        
        if hard_delete:
            db.session.delete(plan)
            logging.info(f"Hard deleted plan {plan_id}")
        else:
            plan.is_active = False
            logging.info(f"Soft deleted plan {plan_id}")
        
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting plan {plan_id}: {str(e)}")
        raise
