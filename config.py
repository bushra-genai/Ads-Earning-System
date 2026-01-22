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
AD_REWARD = 0.10

# Plan configurations
PLANS = {
    'basic': {
        'name': 'Basic',
        'usd': 3,
        'pkr': 840,
        'ads_limit': 1
    },
    'standard': {
        'name': 'Standard',
        'usd': 7,
        'pkr': 1960,
        'ads_limit': 1
    },
    'premium': {
        'name': 'Premium',
        'usd': 10,
        'pkr': 2800,
        'ads_limit': 1
    }
}

# Payment configurations
PAYMENT_METHODS = [
    {
        'id': 'easypaisa',
        'name': 'EasyPaisa',
        'number': '03001234567',
        'title': 'Admin EasyPaisa'
    },
    {
        'id': 'jazzcash',
        'name': 'JazzCash',
        'number': '03007654321',
        'title': 'Admin JazzCash'
    },
    {
        'id': 'bank_transfer',
        'name': 'Bank Transfer',
        'number': '12345678901234',
        'title': 'Admin Bank Account',
        'details': 'Meezan Bank'
    },
    {
        'id': 'crypto',
        'name': 'USDT (TRC20)',
        'number': 'TExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'title': 'Admin USDT Wallet'
    }
]

# Withdrawal configurations
WITHDRAWAL_FEE_PERCENT = 0.05  # 5%
MAX_WITHDRAWAL_REQUESTS_DAILY = 3
MAX_WITHDRAWAL_AMOUNT_PKR = 500
PKR_TO_USD_RATE = 280 # Approximate rate for internal conversion check

# Logging configuration
LOG_FILE = 'app.log'
LOG_LEVEL = 'INFO'