from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from middleware.jwt_required import jwt_required_decorator
from models import db, User, Wallet, Deposit, Withdrawal
from services import withdrawal as withdrawal_service
from datetime import date

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard', methods=['GET'])
@jwt_required_decorator
def dashboard():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        wallet = Wallet.query.filter_by(user_id=user_id).first()
        if not wallet:
            return jsonify({'error': 'Wallet not found'}), 404

        # Team count: count of direct referrals
        team_count = User.query.filter_by(referred_by=user_id).count()

        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'phone': user.phone,
                'referral_code': user.referral_code,
                'plan_active': user.plan_active,
                'status': user.status,
                'created_at': user.created_at.isoformat() if user.created_at else None
            },
            'wallet': {
                'balance': wallet.balance,
                'withdrawable': wallet.withdrawable,
                'total_earned': wallet.total_earned
            },
            'team_count': team_count
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/deposit', methods=['POST'])
@jwt_required_decorator
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

        deposit = Deposit(user_id=user_id, amount=amount, screenshot_url=screenshot_url)
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

        withdrawal_id = withdrawal_service.request_withdrawal(user_id, amount_usd)

        return jsonify({'message': 'Withdrawal requested successfully', 'withdrawal_id': withdrawal_id}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/wallet', methods=['GET'])
@jwt_required_decorator
def wallet_details():
    try:
        user_id = get_jwt_identity()
        wallet = Wallet.query.filter_by(user_id=user_id).first()
        if not wallet:
            return jsonify({'error': 'Wallet not found'}), 404

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
        # Get direct referrals
        referrals = User.query.filter_by(referred_by=user_id).all()
        team = []
        for ref in referrals:
            team.append({
                'id': ref.id,
                'username': ref.username,
                'email': ref.email
            })

        return jsonify({'team': team}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500