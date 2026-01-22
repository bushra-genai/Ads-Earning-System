from app import app
from models import Withdrawal

def list_queued_withdrawals():
    with app.app_context():
        queued = Withdrawal.query.filter_by(status='queued').all()
        if queued:
            print("Queued Withdrawals available for testing:")
            for w in queued:
                print(f" - ID: {w.id}, User ID: {w.user_id}, Amount: {w.amount_usd}")
        else:
            print("No queued withdrawals found. Please create a new withdrawal request from a user account first.")

if __name__ == "__main__":
    list_queued_withdrawals()
