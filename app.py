from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import mysql.connector
from models import db
from routes.auth import auth_bp
from routes.user import user_bp
from routes.ads import ads_bp
from routes.admin import admin_bp
from middleware.rate_limiting import limiter
from middleware.logging import log_request_response

app = Flask(__name__)

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DATABASE'] = 'dailywealth'
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{app.config['MYSQL_USER']}{':' + app.config['MYSQL_PASSWORD'] if app.config['MYSQL_PASSWORD'] else ''}@{app.config['MYSQL_HOST']}/{app.config['MYSQL_DATABASE']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# JWT configuration
app.config['JWT_SECRET_KEY'] = 'dailywealth-secret-key-2026'

# Enable CORS
CORS(app)

# Initialize db
db.init_app(app)
with app.app_context():
    db.create_all()
    # Initialize default plans if none exist
    from services import plan_admin as plan_admin_service
    plan_admin_service.initialize_default_plans()

# Initialize JWT
jwt = JWTManager(app)

# Initialize rate limiter
limiter.init_app(app)

# Initialize logging
log_request_response(app)

from models import TokenBlocklist
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
    return token is not None

from routes.plan import plan_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(ads_bp, url_prefix='/ads')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(plan_bp, url_prefix='/plan')

# Initialize APScheduler
scheduler = BackgroundScheduler()
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True)