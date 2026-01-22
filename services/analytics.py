from datetime import datetime, timedelta
from sqlalchemy import func
from models import db, User, Deposit, Withdrawal, AdsWatch

def get_interval_format(interval):
    """Returns MySQL date format and Python strftime format for the interval."""
    if interval == 'weekly':
        return '%Y-W%u', '%Y-W%u' # Year and Week number
    elif interval == 'monthly':
        return '%Y-%m', '%Y-%m'    # Year and Month
    return '%Y-%m-%d', '%Y-%m-%d'  # Default: Daily

def get_admin_growth_stats(days=30, interval='daily'):
    """
    Get aggregation for system-wide growth metrics based on interval.
    """
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days-1)
    
    db_format, py_format = get_interval_format(interval)
    
    # Queries with grouping based on interval
    # 1. New Users
    new_users = db.session.query(
        func.date_format(User.created_at, db_format).label('bucket'),
        func.count(User.id)
    ).filter(User.created_at >= start_date).group_by('bucket').all()

    # 2. Approved Deposits
    deposits = db.session.query(
        func.date_format(Deposit.created_at, db_format).label('bucket'),
        func.sum(Deposit.amount)
    ).filter(Deposit.status == 'approved', Deposit.created_at >= start_date).group_by('bucket').all()

    # 3. Approved/Paid Withdrawals
    withdrawals = db.session.query(
        func.date_format(Withdrawal.created_at, db_format).label('bucket'),
        func.sum(Withdrawal.amount_usd)
    ).filter(Withdrawal.status.in_(['approved', 'paid']), Withdrawal.created_at >= start_date).group_by('bucket').all()

    # 4. Ad Earnings
    ad_earnings = db.session.query(
        func.date_format(AdsWatch.date, db_format).label('bucket'),
        func.sum(AdsWatch.earned_amount)
    ).filter(AdsWatch.ads_watched > 0, AdsWatch.date >= start_date).group_by('bucket').all()

    # Combine into a chart-ready format
    combined = {}
    
    for b, count in new_users:
        if b not in combined: combined[b] = {"label": b, "new_users": 0, "deposits": 0, "withdrawals": 0, "ad_earnings": 0}
        combined[b]["new_users"] = count

    for b, total in deposits:
        if b not in combined: combined[b] = {"label": b, "new_users": 0, "deposits": 0, "withdrawals": 0, "ad_earnings": 0}
        combined[b]["deposits"] = float(total or 0)

    for b, total in withdrawals:
        if b not in combined: combined[b] = {"label": b, "new_users": 0, "deposits": 0, "withdrawals": 0, "ad_earnings": 0}
        combined[b]["withdrawals"] = float(total or 0)

    for b, total in ad_earnings:
        if b not in combined: combined[b] = {"label": b, "new_users": 0, "deposits": 0, "withdrawals": 0, "ad_earnings": 0}
        combined[b]["ad_earnings"] = float(total or 0)

    return sorted(list(combined.values()), key=lambda x: x['label'])

def get_user_earning_stats(user_id, days=30, interval='daily'):
    """
    Get aggregation for a specific user's earning progress based on interval.
    """
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days-1)
    
    db_format, py_format = get_interval_format(interval)
    
    # Ad Earnings grouped by bucket
    ad_earnings = db.session.query(
        func.date_format(AdsWatch.date, db_format).label('bucket'),
        func.sum(AdsWatch.earned_amount)
    ).filter(AdsWatch.user_id == user_id, AdsWatch.ads_watched > 0, AdsWatch.date >= start_date).group_by('bucket').all()
    
    combined = []
    for b, total in ad_earnings:
        combined.append({
            "label": b,
            "ad_earnings": float(total or 0),
            "total_earnings": float(total or 0)
        })

    return sorted(combined, key=lambda x: x['label'])
