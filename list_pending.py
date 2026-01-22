from app import app
from models import Deposit

def list_pending_deposits():
    with app.app_context():
        pending = Deposit.query.filter_by(status='pending').all()
        if pending:
            print("Pending Deposits available for testing:")
            for d in pending:
                print(f" - ID: {d.id}, User ID: {d.user_id}, Amount: {d.amount}")
        else:
            print("No pending deposits found. Please create a new deposit from a user account first.")

if __name__ == "__main__":
    list_pending_deposits()
