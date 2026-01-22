import logging
from models import db, Withdrawal
from config import WITHDRAWAL_FEE_PERCENT, LOG_FILE, LOG_LEVEL
from .wallet import update_withdrawable_balance

logging.basicConfig(filename=LOG_FILE, level=getattr(logging, LOG_LEVEL), format='%(asctime)s - %(levelname)s - %(message)s')

# Assume exchange rate, or pass it
EXCHANGE_RATE_USD_TO_PKR = 280.0  # Example

from datetime import datetime, date
from sqlalchemy import func
from config import MAX_WITHDRAWAL_REQUESTS_DAILY, MAX_WITHDRAWAL_AMOUNT_PKR, PKR_TO_USD_RATE

def request_withdrawal(user_id, amount_usd):
    """
    Request withdrawal, add to queue.
    """
    try:
        # Check Max Amount in PKR
        # Approximate conversion for limit check
        amount_pkr_approx = amount_usd * PKR_TO_USD_RATE
        if amount_pkr_approx > MAX_WITHDRAWAL_AMOUNT_PKR:
             raise ValueError(f"Withdrawal amount exceeds limit of {MAX_WITHDRAWAL_AMOUNT_PKR} PKR (approx {MAX_WITHDRAWAL_AMOUNT_PKR/PKR_TO_USD_RATE:.2f} USD)")

        # Check Daily Request Limit
        today = date.today()
        daily_requests = Withdrawal.query.filter(
            Withdrawal.user_id == user_id,
            func.date(Withdrawal.created_at) == today
        ).count()
        
        if daily_requests >= MAX_WITHDRAWAL_REQUESTS_DAILY:
            raise ValueError(f"Daily withdrawal limit reached ({MAX_WITHDRAWAL_REQUESTS_DAILY} requests per day)")

        # Calculate fee and PKR amount
        fee = amount_usd * WITHDRAWAL_FEE_PERCENT
        amount_pkr = (amount_usd - fee) * PKR_TO_USD_RATE

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
            raise ValueError(f"Withdrawal {withdrawal_id} has already been {withdrawal.status}")

        # Debit both total balance and withdrawable balance
        from .wallet import update_wallet_balance
        update_wallet_balance(withdrawal.user_id, withdrawal.amount_usd, 'debit')
        update_withdrawable_balance(withdrawal.user_id, withdrawal.amount_usd, 'debit')

        withdrawal.status = 'approved'
        logging.info(f"Withdrawal {withdrawal_id} processed for user {withdrawal.user_id}")
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error processing withdrawal {withdrawal_id}: {str(e)}")
        raise