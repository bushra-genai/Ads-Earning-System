from app import app
from models import db, User, Wallet, Withdrawal

def check_user_finances(user_id):
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            print(f"User {user_id} not found")
            return
        
        wallet = Wallet.query.get(user_id)
        print(f"User: {user.username} (ID: {user_id})")
        if wallet:
            print(f" - Balance: {wallet.balance}")
            print(f" - Withdrawable: {wallet.withdrawable}")
            print(f" - Total Earned: {wallet.total_earned}")
        else:
            print(" - Wallet: Not found")
        
        withdrawals = Withdrawal.query.filter_by(user_id=user_id).all()
        print(f"Withdrawals for user {user_id}:")
        for w in withdrawals:
            print(f" - ID: {w.id}, Amount USD: {w.amount_usd}, Status: {w.status}")

if __name__ == "__main__":
    check_user_finances(1)
