import logging
from models import db, Deposit
from config import LOG_FILE, LOG_LEVEL
from .wallet import update_wallet_balance
from .referral import get_upline, calculate_team_commissions, apply_rank_rewards

logging.basicConfig(filename=LOG_FILE, level=getattr(logging, LOG_LEVEL), format='%(asctime)s - %(levelname)s - %(message)s')

def approve_deposit(deposit_id):
    """
    Approve deposit, credit wallet, commissions, and rank rewards.
    """
    try:
        deposit = Deposit.query.get(deposit_id)
        if not deposit:
            raise ValueError(f"Deposit {deposit_id} not found")

        if deposit.status != 'pending':
            raise ValueError(f"Deposit {deposit_id} is not pending")

        deposit.status = 'approved'

        # Credit deposit amount to user's wallet
        update_wallet_balance(deposit.user_id, deposit.amount, 'credit')

        # Get upline
        upline = get_upline(deposit.user_id)

        # Calculate and credit commissions
        calculate_team_commissions(deposit.amount, upline)

        # Apply rank rewards for each leader
        for leader_id, level in upline:
            apply_rank_rewards(leader_id, deposit.user_id, deposit.amount)

        logging.info(f"Deposit {deposit_id} approved for user {deposit.user_id}, amount {deposit.amount}")
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error approving deposit {deposit_id}: {str(e)}")
        raise