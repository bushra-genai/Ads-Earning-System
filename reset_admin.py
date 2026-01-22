"""
Script to reset admin password or create a new admin user.
Run this script to fix admin login issues.
"""
from app import app
from models import db, User, Wallet
import bcrypt

def reset_admin_password(email, new_password):
    """Reset password for an existing admin"""
    with app.app_context():
        user = User.query.filter_by(email=email, role='admin').first()
        if not user:
            print(f"No admin found with email: {email}")
            return False
        
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user.password_hash = password_hash
        db.session.commit()
        print(f"Password reset successfully for admin: {email}")
        return True

def list_admins():
    """List all admin users"""
    with app.app_context():
        admins = User.query.filter_by(role='admin').all()
        if not admins:
            print("No admin users found in database")
            return []
        
        print("Admin users found:")
        for admin in admins:
            print(f"  - ID: {admin.id}, Username: {admin.username}, Email: {admin.email}")
        return admins

def create_admin(username, email, password):
    """Create a new admin user"""
    with app.app_context():
        # Check if email exists
        if User.query.filter_by(email=email).first():
            print(f"Error: Email {email} already exists")
            return False
        
        if User.query.filter_by(username=username).first():
            print(f"Error: Username {username} already exists")
            return False
        
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        import random, string
        referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            referral_code=referral_code,
            role='admin'
        )
        db.session.add(user)
        db.session.commit()
        
        # Create wallet
        wallet = Wallet(user_id=user.id)
        db.session.add(wallet)
        db.session.commit()
        
        print(f"Admin created successfully: {email}")
        return True

if __name__ == "__main__":
    print("=" * 50)
    print("Admin Password Reset Tool")
    print("=" * 50)
    
    # First, list existing admins
    admins = list_admins()
    
    print("\n" + "=" * 50)
    
    if not admins:
        print("\nCreating new admin user...")
        create_admin("admin", "admin@dailywealth.com", "admin123")
        print("\nNew admin credentials:")
        print("  Email: admin@dailywealth.com")
        print("  Password: admin123")
    else:
        print("\nResetting password for first admin...")
        admin_email = admins[0].email
        reset_admin_password(admin_email, "admin123")
        print(f"\nAdmin credentials:")
        print(f"  Email: {admin_email}")
        print(f"  Password: admin123")
    
    print("\n" + "=" * 50)
    print("Done! You can now login with the above credentials.")
