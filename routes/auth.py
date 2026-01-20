from flask import Blueprint, request, jsonify
import bcrypt
from flask_jwt_extended import create_access_token
import uuid
from models import db, User, Wallet

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')
        referred_by_code = data.get('referred_by')

        if not username or not email or not password:
            return jsonify({'error': 'Username, email, and password are required'}), 400

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400

        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Generate unique referral_code
        referral_code = None
        while True:
            code = uuid.uuid4().hex[:10]
            if not User.query.filter_by(referral_code=code).first():
                referral_code = code
                break

        # Handle referred_by
        referred_by = None
        if referred_by_code:
            referrer = User.query.filter_by(referral_code=referred_by_code).first()
            if referrer:
                referred_by = referrer.id

        # Create user
        role = data.get('role', 'user')
        if role not in ['admin', 'user']:
            role = 'user'

        user = User(
            username=username,
            email=email,
            phone=phone,
            password_hash=password_hash,
            referral_code=referral_code,
            referred_by=referred_by,
            role=role
        )
        db.session.add(user)
        db.session.commit()  # Commit to get user.id

        # Create wallet
        wallet = Wallet(user_id=user.id)
        db.session.add(wallet)
        db.session.commit()

        return jsonify({'message': 'User registered successfully', 'referral_code': referral_code}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        user = User.query.filter_by(email=email).first()
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return jsonify({'error': 'Invalid credentials'}), 401

        access_token = create_access_token(identity=str(user.id))
        return jsonify({'access_token': access_token}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500