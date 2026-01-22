from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, create_access_token, get_jwt, jwt_required
import bcrypt
from middleware.jwt_required import jwt_required_decorator, role_required
from models import db, User, Deposit, Withdrawal, Wallet, TokenBlocklist, Plan
from sqlalchemy import func
from services import deposit as deposit_service
from services import withdrawal as withdrawal_service
from services import analytics as analytics_service
from services import plan_admin as plan_admin_service

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

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
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

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
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

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
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

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
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

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
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

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
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

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/dashboard', methods=['GET'])
@role_required('admin')
def get_dashboard_stats():
    try:
        total_users = User.query.filter_by(role='user').count()
        
        # Financial summary
        total_earnings = db.session.query(func.sum(Wallet.total_earned)).scalar() or 0.0
        total_deposits = db.session.query(func.sum(Deposit.amount)).filter_by(status='approved').scalar() or 0.0
        total_withdrawals = db.session.query(func.sum(Withdrawal.amount_usd)).filter(Withdrawal.status.in_(['approved', 'paid'])).scalar() or 0.0
        
        # Rank Overview logic
        rank_overview = {
            'Bronze': 0, 'Silver': 0, 'Gold': 0, 'Platinum': 0, 'Diamond': 0
        }
        
        return jsonify({
            'stats': {
                'total_users': total_users,
                'total_earnings': round(total_earnings, 2),
                'total_deposits': round(total_deposits, 2),
                'total_withdrawals': round(total_withdrawals, 2)
            },
            'rank_overview': rank_overview
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/referrals', methods=['GET'])
@role_required('admin')
def full_referrals():
    try:
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

@admin_bp.route('/stats/growth', methods=['GET'])
@role_required('admin')
def admin_growth_stats():
    """
    Endpoint for Admin Chart: Growth over time with intervals.
    """
    try:
        days = request.args.get('days', default=30, type=int)
        interval = request.args.get('interval', default='daily')
        stats = analytics_service.get_admin_growth_stats(days, interval)
        return jsonify({'stats': stats}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========== PLAN MANAGEMENT ROUTES ==========

@admin_bp.route('/plans', methods=['GET'])
@role_required('admin')
def list_plans():
    """
    List all plans (including inactive for admin).
    """
    try:
        include_inactive = request.args.get('include_inactive', 'true').lower() == 'true'
        plans = plan_admin_service.get_all_plans(include_inactive=include_inactive)
        return jsonify({
            'plans': [plan.to_dict() for plan in plans]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/plans/<int:plan_id>', methods=['GET'])
@role_required('admin')
def get_plan(plan_id):
    """
    Get a specific plan by ID.
    """
    try:
        plan = plan_admin_service.get_plan_by_id(plan_id)
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404
        return jsonify({'plan': plan.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/plans', methods=['POST'])
@role_required('admin')
def create_plan():
    """
    Create a new plan.
    Required fields: name, slug, price_usd, price_pkr
    Optional fields: ads_limit (default 1), earning_per_ad (default 0.10)
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'slug', 'price_usd', 'price_pkr']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        plan = plan_admin_service.create_plan(
            name=data['name'],
            slug=data['slug'],
            price_usd=float(data['price_usd']),
            price_pkr=float(data['price_pkr']),
            ads_limit=int(data.get('ads_limit', 1)),
            earning_per_ad=float(data.get('earning_per_ad', 0.10))
        )
        
        return jsonify({
            'message': 'Plan created successfully',
            'plan': plan.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/plans/<int:plan_id>', methods=['PUT'])
@role_required('admin')
def update_plan(plan_id):
    """
    Update an existing plan.
    """
    try:
        data = request.get_json()
        
        # Build update kwargs from provided fields
        update_fields = {}
        if 'name' in data:
            update_fields['name'] = data['name']
        if 'slug' in data:
            update_fields['slug'] = data['slug']
        if 'price_usd' in data:
            update_fields['price_usd'] = float(data['price_usd'])
        if 'price_pkr' in data:
            update_fields['price_pkr'] = float(data['price_pkr'])
        if 'ads_limit' in data:
            update_fields['ads_limit'] = int(data['ads_limit'])
        if 'earning_per_ad' in data:
            update_fields['earning_per_ad'] = float(data['earning_per_ad'])
        if 'is_active' in data:
            update_fields['is_active'] = bool(data['is_active'])
        
        if not update_fields:
            return jsonify({'error': 'No fields to update'}), 400
        
        plan = plan_admin_service.update_plan(plan_id, **update_fields)
        
        return jsonify({
            'message': 'Plan updated successfully',
            'plan': plan.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/plans/<int:plan_id>', methods=['DELETE'])
@role_required('admin')
def delete_plan(plan_id):
    """
    Delete a plan (soft delete by default).
    Use ?hard=true for permanent deletion.
    """
    try:
        hard_delete = request.args.get('hard', 'false').lower() == 'true'
        plan_admin_service.delete_plan(plan_id, hard_delete=hard_delete)
        
        return jsonify({
            'message': f'Plan {"permanently deleted" if hard_delete else "deactivated"} successfully'
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500