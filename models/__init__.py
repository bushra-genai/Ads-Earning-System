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