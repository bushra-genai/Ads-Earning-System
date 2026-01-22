import logging
from models import db, User, ReferralTree, RankRewards
from config import REFERRAL_COMMISSIONS, RANK_REWARDS, LOG_FILE, LOG_LEVEL
from .wallet import update_wallet_balance

logging.basicConfig(filename=LOG_FILE, level=getattr(logging, LOG_LEVEL), format='%(asctime)s - %(levelname)s - %(message)s')

def build_referral_tree(user_id, parent_id=None):
    """
    Build referral tree for a user up to 5 levels.
    """
    try:
        if parent_id:
            level = 1
            current_parent = parent_id
            while current_parent and level <= 5:
                referral = ReferralTree(user_id=user_id, parent_id=current_parent, level=level)
                db.session.add(referral)
                current_parent = User.query.get(current_parent).referred_by
                level += 1
        db.session.commit()
        logging.info(f"Referral tree built for user {user_id}")
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error building referral tree for user {user_id}: {str(e)}")
        raise

def get_upline(user_id, max_level=5):
    """
    Get upline users up to max_level.
    Returns list of (user_id, level) tuples.
    """
    upline = []
    current_user = User.query.get(user_id)
    level = 1
    while current_user.referred_by and level <= max_level:
        upline.append((current_user.referred_by, level))
        current_user = User.query.get(current_user.referred_by)
        level += 1
    return upline

def calculate_team_commissions(deposit_amount, upline):
    """
    Calculate and credit commissions to upline.
    """
    try:
        for parent_id, level in upline:
            if level in REFERRAL_COMMISSIONS:
                commission = deposit_amount * REFERRAL_COMMISSIONS[level]
                # Credit both total and withdrawable
                update_wallet_balance(parent_id, commission, 'credit')
                from .wallet import update_withdrawable_balance
                update_withdrawable_balance(parent_id, commission, 'credit')
                logging.info(f"Commission {commission} credited to user {parent_id} for level {level}")
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error calculating commissions: {str(e)}")
        raise

def apply_rank_rewards(leader_id, member_id, member_deposit):
    """
    Apply rank rewards to leader based on member's deposit.
    """
    try:
        # Find the appropriate reward slab
        reward_amount = 0
        for slab in RANK_REWARDS:
            if member_deposit >= slab['min_deposit']:
                reward_amount = slab['reward']
            else:
                break

        if reward_amount > 0:
            # Check if already rewarded? For simplicity, assume apply once per member deposit
            rank_reward = RankRewards(leader_id=leader_id, member_id=member_id, member_deposit=member_deposit, reward_amount=reward_amount)
            db.session.add(rank_reward)
            # Credit both total and withdrawable
            update_wallet_balance(leader_id, reward_amount, 'credit')
            from .wallet import update_withdrawable_balance
            update_withdrawable_balance(leader_id, reward_amount, 'credit')
            logging.info(f"Rank reward {reward_amount} applied to leader {leader_id} for member {member_id}")
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error applying rank rewards: {str(e)}")
        raise