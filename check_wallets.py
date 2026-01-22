from app import app
from models import db, User, Wallet

def check_wallets():
    with app.app_context():
        users = User.query.all()
        print(f"Total Users: {len(users)}")
        missing_wallets = []
        for user in users:
            if not user.wallet:
                missing_wallets.append(user)
        
        print(f"Users missing wallets: {len(missing_wallets)}")
        for user in missing_wallets:
            print(f" - ID: {user.id}, Username: {user.username}, Role: {user.role}")
            # Fix it?
            # wallet = Wallet(user_id=user.id)
            # db.session.add(wallet)
        
        # db.session.commit()

if __name__ == "__main__":
    check_wallets()
