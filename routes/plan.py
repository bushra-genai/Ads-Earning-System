from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Plan
from services import plan as plan_service
from services import plan_admin as plan_admin_service

plan_bp = Blueprint('plan', __name__)

@plan_bp.route('/', methods=['GET'])
def list_plans():
    """
    List all active plans for users.
    """
    try:
        # Initialize default plans if none exist
        plan_admin_service.initialize_default_plans()
        
        plans = plan_admin_service.get_all_plans(include_inactive=False)
        plans_dict = {}
        for plan in plans:
            plans_dict[plan.slug] = {
                'id': plan.id,
                'name': plan.name,
                'usd': plan.price_usd,
                'pkr': plan.price_pkr,
                'ads_limit': plan.ads_limit,
                'earning_per_ad': plan.earning_per_ad
            }
        return jsonify({'plans': plans_dict}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@plan_bp.route('/buy', methods=['POST'])
@jwt_required()
def buy_plan():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        plan_id = data.get('plan_id')  # This is the slug
        screenshot_url = data.get('screenshot_url')

        # Ensure plans exist
        plan_admin_service.initialize_default_plans()

        if not plan_id:
            return jsonify({'error': 'Plan ID is required'}), 400

        if not screenshot_url:
            return jsonify({'error': 'Screenshot URL is required'}), 400

        # Get plan from database by slug
        plan = plan_admin_service.get_plan_by_slug(plan_id)
        if not plan:
            available_plans = [p.slug for p in plan_admin_service.get_all_plans()]
            return jsonify({'error': f'Invalid plan ID: {plan_id}. Available plans: {", ".join(available_plans)}'}), 400

        deposit = plan_service.purchase_plan(user_id, plan_id, screenshot_url)
        
        return jsonify({
            'message': 'Plan purchase initiated. Please wait for admin approval.',
            'deposit_id': deposit.id,
            'amount': plan.price_usd,
            'pkr_amount': plan.price_pkr,
            'payment_options': {
                'JazzCash': '03001234567',
                'EasyPaisa': '03001234567',
                'Bank Transfer': 'HBL 1234567890',
                'Crypto': 'USDT-TRC20 Address Here'
            }
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

