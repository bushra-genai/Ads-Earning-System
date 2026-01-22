from app import app
from models import db, Wallet

def sync_all_wallets():
    with app.app_context():
        wallets = Wallet.query.all()
        print(f"Checking {len(wallets)} wallets for synchronization...")
        
        for wallet in wallets:
            if wallet.balance > wallet.withdrawable:
                old_withdrawable = wallet.withdrawable
                wallet.withdrawable = wallet.balance
                print(f" - Corrected Wallet for User {wallet.user_id}: {old_withdrawable} -> {wallet.withdrawable}")
        
        db.session.commit()
        print("Finical Flow Synchronization Complete.")

if __name__ == "__main__":
    sync_all_wallets()
