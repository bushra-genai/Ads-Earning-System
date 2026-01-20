from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from middleware.jwt_required import jwt_required_decorator
from models import db, AdsWatch
from services import ads as ads_service
from datetime import date

ads_bp = Blueprint('ads', __name__)

@ads_bp.route('/watch-ad', methods=['POST'])
@jwt_required_decorator
def watch_ad():
    try:
        user_id = get_jwt_identity()
        # Assuming the timer is handled on frontend, credit immediately
        ads_service.watch_ad(user_id)
        return jsonify({'message': 'Ad watched successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ads_bp.route('/ad-status', methods=['GET'])
@jwt_required_decorator
def ad_status():
    try:
        user_id = get_jwt_identity()
        today = date.today()
        ad_watch = AdsWatch.query.filter_by(user_id=user_id, date=today).first()
        can_watch = not ad_watch or not ad_watch.watched
        return jsonify({'can_watch': can_watch}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500