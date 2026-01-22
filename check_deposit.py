from app import app
from models import Deposit

def check_deposit(deposit_id):
    with app.app_context():
        deposit = Deposit.query.get(deposit_id)
        if deposit:
            print(f"Deposit {deposit_id} status: {deposit.status}")
        else:
            print(f"Deposit {deposit_id} not found")

if __name__ == "__main__":
    import sys
    dep_id = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    check_deposit(dep_id)
