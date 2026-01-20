from app import app
from models import db, User

with app.app_context():
    users = User.query.all()
    print("ID | Username | Email | Role")
    print("-" * 30)
    for user in users:
        print(f"{user.id} | {user.username} | {user.email} | {user.role}")
