import os

# Commission percentages for referral levels (1-5)
REFERRAL_COMMISSIONS = {
    1: 0.10,  # 10%
    2: 0.05,  # 5%
    3: 0.03,  # 3%
    4: 0.02,  # 2%
    5: 0.01   # 1%
}

# Rank reward slabs based on team deposits
RANK_REWARDS = [
    {'min_deposit': 0, 'reward': 0},
    {'min_deposit': 1000, 'reward': 50},
    {'min_deposit': 5000, 'reward': 200},
    {'min_deposit': 10000, 'reward': 500},
    {'min_deposit': 25000, 'reward': 1000},
    {'min_deposit': 50000, 'reward': 2000},
]

# Ad watching reward per ad
AD_REWARD = 0.50

# Withdrawal fee percentage
WITHDRAWAL_FEE_PERCENT = 0.05  # 5%

# Logging configuration
LOG_FILE = 'app.log'
LOG_LEVEL = 'INFO'