from flask import Blueprint, request, jsonify
import bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity
from models import db, User, Wallet, TokenBlocklist
import random
import string

auth_bp = Blueprint('auth', __name__)

def generate_referral_code(length=8):
    """Generate a unique alphanumeric referral code."""
    characters = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choices(characters, k=length))
        # Check if code is unique
        if not User.query.filter_by(referral_code=code).first():
            return code

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')
        referred_by = data.get('referred_by')
        
        # Convert empty string to None for referred_by
        if referred_by == '' or not referred_by:
            referred_by = None

        if not username or not email or not password:
            return jsonify({'error': 'Username, email, and password are required'}), 400

        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already taken'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400

        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Generate unique referral code
        referral_code = generate_referral_code()

        # Role handling
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

@auth_bp.route('/admin/register', methods=['POST'])
def register_admin():
    try:
        data = request.get_json()
        # Admin Secret Key for protection
        admin_secret = data.get('admin_secret')
        if admin_secret != "DAILYWEALTH_ADMIN_2026": # In production, use env var
            return jsonify({'error': 'Unauthorized registration attempt'}), 403

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({'error': 'Username, email, and password are required'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already taken'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400

        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Generate unique referral code (even for admin)
        referral_code = generate_referral_code()

        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            referral_code=referral_code,
            role='admin'
        )
        db.session.add(user)
        db.session.commit()

        # Create wallet for admin
        wallet = Wallet(user_id=user.id)
        db.session.add(wallet)
        db.session.commit()

        return jsonify({'message': 'Admin registered successfully'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        jti = get_jwt()['jti']
        db.session.add(TokenBlocklist(jti=jti))
        db.session.commit()
        return jsonify({'message': 'Successfully logged out'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        user = User.query.filter_by(email=email, role='admin').first()
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return jsonify({'error': 'Invalid admin credentials'}), 401

        access_token = create_access_token(identity=str(user.id))
        return jsonify({'access_token': access_token}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if not old_password or not new_password:
            return jsonify({'error': 'Old password and new password are required'}), 400

        user = User.query.get(int(user_id))
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Verify old password
        if not bcrypt.checkpw(old_password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return jsonify({'error': 'Old password is incorrect'}), 401

        # Update to new password
        new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user.password_hash = new_password_hash
        db.session.commit()

        return jsonify({'message': 'Password changed successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            # For security, don't reveal if email exists
            return jsonify({'message': 'If the email exists, a reset link has been sent'}), 200

        # Mock implementation - In production, send email with reset token
        # For now, just return a success message
        return jsonify({
            'message': 'Password reset instructions have been sent to your email',
            'note': 'This is a mock implementation. Contact admin for password reset.'
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/admin/logout', methods=['POST'])
@jwt_required()
def admin_logout():
    try:
        # Verify it's an admin
        user_id = get_jwt_identity()
        try:
            user = User.query.get(int(user_id))
        except (ValueError, TypeError):
            user = User.query.get(user_id)
            
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        jti = get_jwt()['jti']
        db.session.add(TokenBlocklist(jti=jti))
        db.session.commit()
        return jsonify({'message': 'Admin successfully logged out'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/admin/change-password', methods=['POST'])
@jwt_required()
def admin_change_password():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if not old_password or not new_password:
            return jsonify({'error': 'Old password and new password are required'}), 400

        user = User.query.get(int(user_id))
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        # Verify old password
        if not bcrypt.checkpw(old_password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return jsonify({'error': 'Old password is incorrect'}), 401

        # Update to new password
        new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user.password_hash = new_password_hash
        db.session.commit()

        return jsonify({'message': 'Admin password changed successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/admin/forgot-password', methods=['POST'])
def admin_forgot_password():
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        user = User.query.filter_by(email=email, role='admin').first()
        if not user:
            # For security, don't reveal if admin email exists
            return jsonify({'message': 'If the admin email exists, a reset link has been sent'}), 200

        # Mock implementation - In production, send email with reset token
        return jsonify({
            'message': 'Admin password reset instructions have been sent to your email',
            'note': 'This is a mock implementation. Contact super admin for password reset.'
        }), 200

    except Exception as e:
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