import logging
from models import db, Wallet
from config import LOG_FILE, LOG_LEVEL

logging.basicConfig(filename=LOG_FILE, level=getattr(logging, LOG_LEVEL), format='%(asctime)s - %(levelname)s - %(message)s')

def update_wallet_balance(user_id, amount, operation='credit'):
    """
    Transaction-safe wallet balance update.
    :param user_id: User ID
    :param amount: Amount to credit or debit
    :param operation: 'credit' or 'debit'
    """
    try:
        user_id = int(user_id)
        wallet = Wallet.query.filter_by(user_id=user_id).first()
        if not wallet:
            # Lazy Wallet Creation for all operations
            wallet = Wallet(user_id=user_id, balance=0.0, withdrawable=0.0, total_earned=0.0)
            db.session.add(wallet)
            # We don't commit yet to keep it part of the larger transaction if any

        if operation == 'credit':
            wallet.balance += amount
            wallet.total_earned += amount
            logging.info(f"Credited {amount} to user {user_id}. New balance: {wallet.balance}")
        elif operation == 'debit':
            if wallet.balance < amount:
                raise ValueError(f"Insufficient balance for user {user_id}")
            wallet.balance -= amount
            logging.info(f"Debited {amount} from user {user_id}. New balance: {wallet.balance}")
        else:
            raise ValueError("Invalid operation")

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating wallet for user {user_id}: {str(e)}")
        raise

def update_withdrawable_balance(user_id, amount, operation='credit'):
    """
    Update withdrawable balance.
    :param user_id: User ID
    :param amount: Amount to credit or debit
    :param operation: 'credit' or 'debit'
    """
    try:
        user_id = int(user_id)
        wallet = Wallet.query.filter_by(user_id=user_id).first()
        if not wallet:
            # Lazy Wallet Creation
            wallet = Wallet(user_id=user_id, balance=0.0, withdrawable=0.0, total_earned=0.0)
            db.session.add(wallet)

        if operation == 'credit':
            wallet.withdrawable += amount
            logging.info(f"Credited withdrawable {amount} to user {user_id}. New withdrawable: {wallet.withdrawable}")
        elif operation == 'debit':
            if wallet.withdrawable < amount:
                raise ValueError(f"Insufficient withdrawable balance for user {user_id}")
            wallet.withdrawable -= amount
            logging.info(f"Debited withdrawable {amount} from user {user_id}. New withdrawable: {wallet.withdrawable}")
        else:
            raise ValueError("Invalid operation")

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating withdrawable for user {user_id}: {str(e)}")
        raise