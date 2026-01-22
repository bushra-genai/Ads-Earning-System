from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from middleware.jwt_required import jwt_required_decorator, plan_required
from models import db, User, Wallet, Deposit, Withdrawal
from services import withdrawal as withdrawal_service
from services import analytics as analytics_service
from datetime import date

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard', methods=['GET'])
@jwt_required_decorator
def dashboard():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user:
            return jsonify({'error': 'User not found'}), 404

        wallet = Wallet.query.filter_by(user_id=int(user_id)).first()
        if not wallet:
            # Lazy Wallet Creation
            wallet = Wallet(user_id=int(user_id))
            db.session.add(wallet)
            db.session.commit()

        # Direct referrals count
        direct_referrals_count = User.query.filter_by(referred_by=int(user_id)).count()

        # Calculate team earnings and stats recursively (up to 5 levels)
        def calculate_team_stats(parent_id, current_level=1, max_level=5):
            """Recursively calculate team stats by level"""
            if current_level > max_level:
                return {'earnings': 0.0, 'count': 0, 'active_plans': 0}
            
            # Get direct referrals for this parent
            referrals = User.query.filter_by(referred_by=parent_id).all()
            level_earnings = 0.0
            level_count = len(referrals)
            active_plans = 0
            
            for ref in referrals:
                # Get wallet info
                ref_wallet = Wallet.query.filter_by(user_id=ref.id).first()
                if ref_wallet:
                    level_earnings += ref_wallet.total_earned
                
                if ref.plan_status == 'active':
                    active_plans += 1
                
                # Add stats from downline
                downline_stats = calculate_team_stats(ref.id, current_level + 1, max_level)
                level_earnings += downline_stats['earnings']
                level_count += downline_stats['count']
                active_plans += downline_stats['active_plans']
            
            return {
                'earnings': level_earnings,
                'count': level_count,
                'active_plans': active_plans
            }
        
        # Get per-level breakdown
        def get_level_breakdown(parent_id, max_level=5):
            """Get earnings breakdown per level"""
            levels_data = {}
            
            def process_level(parent_id, current_level):
                if current_level > max_level:
                    return
                
                referrals = User.query.filter_by(referred_by=parent_id).all()
                
                if current_level not in levels_data:
                    levels_data[current_level] = {
                        'count': 0,
                        'earnings': 0.0,
                        'active_plans': 0
                    }
                
                for ref in referrals:
                    levels_data[current_level]['count'] += 1
                    ref_wallet = Wallet.query.filter_by(user_id=ref.id).first()
                    if ref_wallet:
                        levels_data[current_level]['earnings'] += ref_wallet.total_earned
                    if ref.plan_status == 'active':
                        levels_data[current_level]['active_plans'] += 1
                    
                    # Process next level for this referral's downline
                    process_level(ref.id, current_level + 1)
            
            process_level(parent_id, 1)
            return levels_data
        
        team_stats = calculate_team_stats(int(user_id))
        level_breakdown = get_level_breakdown(int(user_id))

        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'phone': user.phone,
                'referral_code': user.referral_code,
                'active_plan': user.active_plan,
                'plan_status': user.plan_status,
                'status': user.status,
                'created_at': user.created_at.isoformat() if user.created_at else None
            },
            'wallet': {
                'balance': wallet.balance,
                'withdrawable': wallet.withdrawable,
                'total_earned': wallet.total_earned
            },
            'team': {
                'direct_referrals': direct_referrals_count,
                'total_team_size': team_stats['count'],
                'total_team_earnings': round(team_stats['earnings'], 2),
                'active_plans_in_team': team_stats['active_plans'],
                'level_breakdown': {
                    f'level_{level}': {
                        'count': data['count'],
                        'earnings': round(data['earnings'], 2),
                        'active_plans': data['active_plans']
                    } for level, data in level_breakdown.items()
                }
            },
            # Keep backward compatibility
            'team_count': direct_referrals_count,
            'team_earnings': round(team_stats['earnings'], 2)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/payment-methods', methods=['GET'])
@jwt_required_decorator
def payment_methods():
    try:
        from config import PAYMENT_METHODS
        return jsonify({'payment_methods': PAYMENT_METHODS}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/deposit', methods=['POST'])
@plan_required
def deposit():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        amount = data.get('amount')
        screenshot_url = data.get('screenshot_url')

        if not amount or amount <= 0:
            return jsonify({'error': 'Valid amount is required'}), 400

        if not screenshot_url:
            return jsonify({'error': 'Screenshot URL is required'}), 400

        deposit = Deposit(user_id=int(user_id), amount=amount, screenshot_url=screenshot_url)
        db.session.add(deposit)
        db.session.commit()

        return jsonify({'message': 'Deposit submitted successfully', 'deposit_id': deposit.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/withdraw', methods=['POST'])
@jwt_required_decorator
def withdraw():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        amount_usd = data.get('amount_usd')

        if not amount_usd or amount_usd <= 0:
            return jsonify({'error': 'Valid amount in USD is required'}), 400

        withdrawal_id = withdrawal_service.request_withdrawal(int(user_id), amount_usd)

        return jsonify({'message': 'Withdrawal requested successfully', 'withdrawal_id': withdrawal_id}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/wallet', methods=['GET'])
@jwt_required_decorator
def wallet_details():
    try:
        user_id = get_jwt_identity()
        wallet = Wallet.query.filter_by(user_id=int(user_id)).first()
        if not wallet:
            # Lazy Wallet Creation
            wallet = Wallet(user_id=int(user_id))
            db.session.add(wallet)
            db.session.commit()

        return jsonify({
            'balance': wallet.balance,
            'withdrawable': wallet.withdrawable,
            'total_earned': wallet.total_earned
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/team', methods=['GET'])
@jwt_required_decorator
def team():
    try:
        user_id = get_jwt_identity()
        
        def get_team_recursive(parent_id, current_level=1, max_level=5):
            """Recursively get team members up to max_level"""
            if current_level > max_level:
                return []
            
            # Get direct referrals for this parent
            referrals = User.query.filter_by(referred_by=parent_id).all()
            team_members = []
            
            for ref in referrals:
                # Get wallet info
                wallet = Wallet.query.filter_by(user_id=ref.id).first()
                
                member_info = {
                    'id': ref.id,
                    'username': ref.username,
                    'email': ref.email,
                    'phone': ref.phone,
                    'referral_code': ref.referral_code,
                    'level': current_level,
                    'active_plan': ref.active_plan,
                    'plan_status': ref.plan_status,
                    'status': ref.status,
                    'total_earned': wallet.total_earned if wallet else 0,
                    'balance': wallet.balance if wallet else 0,
                    'created_at': ref.created_at.isoformat() if ref.created_at else None,
                    'downline': get_team_recursive(ref.id, current_level + 1, max_level)
                }
                team_members.append(member_info)
            
            return team_members
        
        # Get all team levels starting from current user
        team_structure = get_team_recursive(int(user_id))
        
        # Calculate statistics by level
        level_stats = {}
        def calculate_stats(members, stats_dict):
            for member in members:
                level = member['level']
                if level not in stats_dict:
                    stats_dict[level] = {
                        'count': 0,
                        'active_plans': 0,
                        'total_earnings': 0
                    }
                stats_dict[level]['count'] += 1
                if member['plan_status'] == 'active':
                    stats_dict[level]['active_plans'] += 1
                stats_dict[level]['total_earnings'] += member['total_earned']
                
                # Recursively calculate for downline
                if member['downline']:
                    calculate_stats(member['downline'], stats_dict)
        
        calculate_stats(team_structure, level_stats)
        
        # Calculate total team size
        def count_total(members):
            total = len(members)
            for member in members:
                if member['downline']:
                    total += count_total(member['downline'])
            return total
        
        total_team_size = count_total(team_structure)
        
        return jsonify({
            'team': team_structure,
            'total_team_size': total_team_size,
            'level_statistics': level_stats
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/stats/earnings', methods=['GET'])
@jwt_required_decorator
def user_earning_stats():
    """
    Endpoint for User Chart: Earning progress over time with intervals.
    """
    try:
        user_id = get_jwt_identity()
        days = request.args.get('days', default=30, type=int)
        interval = request.args.get('interval', default='daily')
        stats = analytics_service.get_user_earning_stats(int(user_id), days, interval)
        return jsonify({'stats': stats}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500