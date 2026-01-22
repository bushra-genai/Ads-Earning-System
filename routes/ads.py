from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from middleware.jwt_required import jwt_required_decorator, plan_required
from models import db, AdsWatch
from services import ads as ads_service
from datetime import date

ads_bp = Blueprint('ads', __name__)

@ads_bp.route('/watch-ad', methods=['POST'])
@plan_required
def watch_ad():
    try:
        user_id = get_jwt_identity()
        # Assuming the timer is handled on frontend, credit immediately
        ads_service.watch_ad(int(user_id))
        return jsonify({'message': 'Ad watched successfully'}), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ads_bp.route('/ad-status', methods=['GET'])
@plan_required
def ad_status():
    try:
        user_id = get_jwt_identity()
        from models import User
        user = User.query.get(int(user_id))
        
        today = date.today()
        ad_watch = AdsWatch.query.filter_by(user_id=int(user_id), date=today).first()
        
        ads_watched_today = ad_watch.ads_watched if ad_watch else 0
        can_watch = ads_watched_today < user.daily_ads_limit
        
        return jsonify({
            'can_watch': can_watch,
            'ads_watched_today': ads_watched_today,
            'daily_ads_limit': user.daily_ads_limit,
            'remaining_ads': user.daily_ads_limit - ads_watched_today
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ads_bp.route('/reset-ad', methods=['POST'])
@jwt_required_decorator
def reset_ad():
    """
    Test endpoint to reset ad watch status for the current user for today.
    """
    try:
        user_id = get_jwt_identity()
        today = date.today()
        ad_watch = AdsWatch.query.filter_by(user_id=int(user_id), date=today).first()
        
        if ad_watch:
            db.session.delete(ad_watch)
            db.session.commit()
            return jsonify({'message': 'Ad watch status reset successfully for today'}), 200
        
        return jsonify({'message': 'No ad watch record found for today'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500