from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify
from functools import wraps
from models import User

def jwt_required_decorator(f):
    """
    Decorator to require JWT token for accessing protected routes.
    """
    @jwt_required()
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper

def role_required(role):
    """
    Decorator to require a specific role for accessing routes.
    """
    def decorator(f):
        @jwt_required()
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            # Explicitly cast to int for better compatibility with User.query.get
            try:
                user = User.query.get(int(user_id))
            except (ValueError, TypeError):
                user = User.query.get(user_id)
                
            if not user:
                return jsonify({'error': 'User not found'}), 401
            
            if user.role != role:
                from flask import current_app
                current_app.logger.info(f"Access denied for user {user_id} (Role: {user.role}). Required: {role}")
                return jsonify({'error': f'{role.capitalize()} access required'}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

def plan_required(f):
    """
    Decorator to require an active plan for accessing certain routes.
    """
    @jwt_required()
    @wraps(f)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        try:
            user = User.query.get(int(user_id))
        except (ValueError, TypeError):
            user = User.query.get(user_id)
            
        if not user:
            return jsonify({'error': 'User not found'}), 401
        
        # Admin is always allowed
        if user.role == 'admin':
            return f(*args, **kwargs)

        if user.plan_status != 'active':
            return jsonify({
                'error': 'Plan required',
                'message': 'Please buy a plan to start earning.'
            }), 403
            
        return f(*args, **kwargs)
    return wrapper