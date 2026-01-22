from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models to register them
from .user import User
from .wallet import Wallet
from .deposit import Deposit
from .withdrawal import Withdrawal
from .ads_watch import AdsWatch
from .referral_tree import ReferralTree
from .rank_rewards import RankRewards
from .token_blocklist import TokenBlocklist
from .plan import Plan

__all__ = ['db', 'User', 'Wallet', 'Deposit', 'Withdrawal', 'AdsWatch', 'ReferralTree', 'RankRewards', 'TokenBlocklist', 'Plan']