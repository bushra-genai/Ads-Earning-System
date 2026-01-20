from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from middleware.jwt_required import jwt_required_decorator, role_required
from models import db, User, Deposit, Withdrawal
from services import deposit as deposit_service
from services import withdrawal as withdrawal_service

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
@role_required('admin')
def list_users():
    try:
        users = User.query.all()
        user_list = []
        for user in users:
            user_list.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'phone': user.phone,
                'role': user.role,
                'status': user.status,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        return jsonify({'users': user_list}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/deposit/approve', methods=['POST'])
@role_required('admin')
def approve_deposit():
    try:
        data = request.get_json()
        deposit_id = data.get('deposit_id')
        if not deposit_id:
            return jsonify({'error': 'Deposit ID required'}), 400

        deposit_service.approve_deposit(deposit_id)
        return jsonify({'message': 'Deposit approved successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/deposit/reject', methods=['POST'])
@role_required('admin')
def reject_deposit():
    try:
        data = request.get_json()
        deposit_id = data.get('deposit_id')
        if not deposit_id:
            return jsonify({'error': 'Deposit ID required'}), 400

        deposit = Deposit.query.get(deposit_id)
        if not deposit:
            return jsonify({'error': 'Deposit not found'}), 404

        deposit.status = 'rejected'
        db.session.commit()
        return jsonify({'message': 'Deposit rejected successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/withdraw/approve', methods=['POST'])
@role_required('admin')
def approve_withdrawal():
    try:
        data = request.get_json()
        withdrawal_id = data.get('withdrawal_id')
        if not withdrawal_id:
            return jsonify({'error': 'Withdrawal ID required'}), 400

        withdrawal_service.process_withdrawal(withdrawal_id)
        return jsonify({'message': 'Withdrawal approved successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/withdraw/reject', methods=['POST'])
@role_required('admin')
def reject_withdrawal():
    try:
        data = request.get_json()
        withdrawal_id = data.get('withdrawal_id')
        if not withdrawal_id:
            return jsonify({'error': 'Withdrawal ID required'}), 400

        withdrawal = Withdrawal.query.get(withdrawal_id)
        if not withdrawal:
            return jsonify({'error': 'Withdrawal not found'}), 404

        withdrawal.status = 'rejected'
        db.session.commit()
        return jsonify({'message': 'Withdrawal rejected successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/user/ban', methods=['POST'])
@role_required('admin')
def ban_user():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        user.status = 'banned'
        db.session.commit()
        return jsonify({'message': 'User banned successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/user/freeze', methods=['POST'])
@role_required('admin')
def freeze_user():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        user.status = 'suspended'
        db.session.commit()
        return jsonify({'message': 'User frozen successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/referrals', methods=['GET'])
@role_required('admin')
def full_referrals():
    try:
        # Simple list of all users with their referred_by
        users = User.query.all()
        referrals = []
        for user in users:
            referrals.append({
                'id': user.id,
                'username': user.username,
                'referred_by': user.referred_by
            })
        return jsonify({'referrals': referrals}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500