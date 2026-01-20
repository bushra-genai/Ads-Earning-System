from app import app
from models import db, User
import sys

def make_admin(email):
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"User with email {email} not found.")
            return
        
        user.role = 'admin'
        db.session.commit()
        print(f"User {email} has been promoted to admin successfully.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python make_admin.py <email>")
    else:
        make_admin(sys.argv[1])
