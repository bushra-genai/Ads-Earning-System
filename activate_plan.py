"""
Script to manually activate a user's plan for testing purposes.
"""
from app import app
from models import db, User

def activate_user_plan(user_id, plan_slug='basic'):
    """Activate a plan for a user directly (bypassing payment)"""
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            print(f"User {user_id} not found")
            return False
        
        user.plan_status = 'active'
        user.active_plan = plan_slug
        user.ads_permission = True
        user.daily_ads_limit = 1  # 1 ad per day as per requirements
        
        db.session.commit()
        print(f"Plan '{plan_slug}' activated for user: {user.username} (ID: {user_id})")
        print(f"  - Plan status: active")
        print(f"  - Ads permission: True")
        print(f"  - Daily ads limit: 1")
        return True

def list_users():
    """List all users and their plan status"""
    with app.app_context():
        users = User.query.all()
        print("\nAll users:")
        print("-" * 70)
        for u in users:
            print(f"ID: {u.id}, Username: {u.username}, Role: {u.role}, Plan: {u.active_plan}, Status: {u.plan_status}")
        print("-" * 70)
        return users

if __name__ == "__main__":
    print("=" * 50)
    print("Activate User Plan Tool")
    print("=" * 50)
    
    # List all users
    users = list_users()
    
    # Activate plan for all non-admin users
    with app.app_context():
        non_admin_users = User.query.filter_by(role='user').all()
        if non_admin_users:
            for user in non_admin_users:
                if user.plan_status != 'active':
                    activate_user_plan(user.id, 'basic')
            print("\nDone! All users now have active plans.")
        else:
            print("\nNo regular users found. Create a user first via /auth/register")
