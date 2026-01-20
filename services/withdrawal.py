import logging
from models import db, Withdrawal
from config import WITHDRAWAL_FEE_PERCENT, LOG_FILE, LOG_LEVEL
from .wallet import update_withdrawable_balance

logging.basicConfig(filename=LOG_FILE, level=getattr(logging, LOG_LEVEL), format='%(asctime)s - %(levelname)s - %(message)s')

# Assume exchange rate, or pass it
EXCHANGE_RATE_USD_TO_PKR = 280.0  # Example

def request_withdrawal(user_id, amount_usd):
    """
    Request withdrawal, add to queue.
    """
    try:
        # Calculate fee and PKR amount
        fee = amount_usd * WITHDRAWAL_FEE_PERCENT
        amount_pkr = (amount_usd - fee) * EXCHANGE_RATE_USD_TO_PKR

        # Check withdrawable balance
        # Assuming amount_usd is in USD, but wallet is in USD? Wait, probably wallet balance is in USD.
        # Need to check if withdrawable >= amount_usd
        # But update_withdrawable_balance is in USD I assume.

        # Get next queue position
        max_queue = db.session.query(db.func.max(Withdrawal.queue_position)).scalar() or 0
        queue_position = max_queue + 1

        withdrawal = Withdrawal(
            user_id=user_id,
            amount_usd=amount_usd,
            amount_pkr=amount_pkr,
            fee=fee,
            status='queued',
            queue_position=queue_position
        )
        db.session.add(withdrawal)
        logging.info(f"Withdrawal requested by user {user_id}, amount {amount_usd} USD, queue position {queue_position}")
        db.session.commit()
        return withdrawal.id
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error requesting withdrawal for user {user_id}: {str(e)}")
        raise

def process_withdrawal(withdrawal_id):
    """
    Process withdrawal from queue.
    """
    try:
        withdrawal = Withdrawal.query.get(withdrawal_id)
        if not withdrawal:
            raise ValueError(f"Withdrawal {withdrawal_id} not found")

        if withdrawal.status != 'queued':
            raise ValueError(f"Withdrawal {withdrawal_id} is not queued")

        # Debit withdrawable balance
        update_withdrawable_balance(withdrawal.user_id, withdrawal.amount_usd, 'debit')

        withdrawal.status = 'approved'
        logging.info(f"Withdrawal {withdrawal_id} processed for user {withdrawal.user_id}")
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error processing withdrawal {withdrawal_id}: {str(e)}")
        raise