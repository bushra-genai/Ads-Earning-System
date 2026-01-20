# DailyWealth App - Complete Documentation

## 📋 Project Overview
**DailyWealth** ek Flask-based web application hai jo MLM (Multi-Level Marketing) system implement karta hai. Isme users deposit kar sakte hain, ads dekh sakte hain, referrals kar sakte hain, aur commissions earn kar sakte hain.

## 🏗️ Project Structure
```
dailywealth/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Dependencies
├── middleware/           # Custom middleware
├── models/              # Database models
├── routes/              # API endpoints
├── services/            # Business logic
└── utils/               # Utility functions
```

## 🔧 Technology Stack
- **Backend**: Flask (Python)
- **Database**: MySQL with SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens)
- **Scheduler**: APScheduler
- **Rate Limiting**: Flask-Limiter
- **CORS**: Flask-CORS

## 📦 Dependencies (requirements.txt)
```
Flask
Flask-JWT-Extended
bcrypt
mysql-connector-python
APScheduler
Flask-CORS
Flask-SQLAlchemy
Flask-Limiter
```

## ⚙️ Configuration (config.py)

### Referral Commission Structure
```python
REFERRAL_COMMISSIONS = {
    1: 0.10,  # Level 1: 10%
    2: 0.05,  # Level 2: 5%
    3: 0.03,  # Level 3: 3%
    4: 0.02,  # Level 4: 2%
    5: 0.01   # Level 5: 1%
}
```

### Rank Rewards System
```python
RANK_REWARDS = [
    {'min_deposit': 0, 'reward': 0},
    {'min_deposit': 1000, 'reward': 50},
    {'min_deposit': 5000, 'reward': 200},
    {'min_deposit': 10000, 'reward': 500},
    {'min_deposit': 25000, 'reward': 1000},
    {'min_deposit': 50000, 'reward': 2000},
]
```

### Other Settings
- **Ad Reward**: $0.50 per ad
- **Withdrawal Fee**: 5%
- **Exchange Rate**: 1 USD = 280 PKR

## 🗄️ Database Models

### 1. User Model (`models/user.py`)
```python
class User:
    - id (Primary Key)
    - username (Unique)
    - email (Unique)
    - phone
    - password_hash
    - referral_code (Unique)
    - referred_by (Foreign Key to User)
    - plan_active (Boolean)
    - role (admin/user)
    - status (active/suspended/banned)
    - created_at
    - last_active
```

### 2. Wallet Model (`models/wallet.py`)
```python
class Wallet:
    - user_id (Primary Key, Foreign Key)
    - balance (Total balance)
    - withdrawable (Withdrawable amount)
    - total_earned (Lifetime earnings)
```

### 3. Deposit Model (`models/deposit.py`)
```python
class Deposit:
    - id (Primary Key)
    - user_id (Foreign Key)
    - amount
    - screenshot_url
    - status (pending/approved/rejected)
    - created_at
```

### 4. Withdrawal Model (`models/withdrawal.py`)
```python
class Withdrawal:
    - id (Primary Key)
    - user_id (Foreign Key)
    - amount_usd
    - amount_pkr
    - fee
    - status (queued/approved/paid/rejected)
    - queue_position
    - created_at
```

### 5. AdsWatch Model (`models/ads_watch.py`)
```python
class AdsWatch:
    - user_id (Primary Key)
    - date (Primary Key)
    - watched (Boolean)
    - earned_amount
```

### 6. ReferralTree Model (`models/referral_tree.py`)
```python
class ReferralTree:
    - user_id (Primary Key)
    - parent_id (Foreign Key)
    - level (1-5)
```

### 7. RankRewards Model (`models/rank_rewards.py`)
```python
class RankRewards:
    - id (Primary Key)
    - leader_id (Foreign Key)
    - member_id (Foreign Key)
    - member_deposit
    - reward_amount
    - created_at
```

## 🛣️ API Routes

### Authentication Routes (`routes/auth.py`)

#### POST `/auth/register`
**Purpose**: User registration
**Input**:
```json
{
    "username": "string",
    "email": "string",
    "phone": "string",
    "password": "string",
    "referred_by": "referral_code"
}
```
**Output**: Success message + referral_code

#### POST `/auth/login`
**Purpose**: User login
**Input**:
```json
{
    "email": "string",
    "password": "string"
}
```
**Output**: JWT access_token

### User Routes (`routes/user.py`)

#### GET `/user/dashboard`
**Purpose**: User dashboard data
**Auth**: JWT Required
**Output**: User info, wallet details, team count

#### POST `/user/deposit`
**Purpose**: Submit deposit request
**Auth**: JWT Required
**Input**:
```json
{
    "amount": "number",
    "screenshot_url": "string"
}
```

#### POST `/user/withdraw`
**Purpose**: Request withdrawal
**Auth**: JWT Required
**Input**:
```json
{
    "amount_usd": "number"
}
```

#### GET `/user/wallet`
**Purpose**: Wallet details
**Auth**: JWT Required
**Output**: Balance, withdrawable, total_earned

#### GET `/user/team`
**Purpose**: Direct referrals list
**Auth**: JWT Required
**Output**: Team members list

### Admin Routes (`routes/admin.py`)

#### GET `/admin/users`
**Purpose**: List all users
**Auth**: Admin Role Required
**Output**: All users list

#### POST `/admin/deposit/approve`
**Purpose**: Approve deposit
**Auth**: Admin Required
**Input**: `{"deposit_id": "number"}`

#### POST `/admin/deposit/reject`
**Purpose**: Reject deposit
**Auth**: Admin Required
**Input**: `{"deposit_id": "number"}`

#### POST `/admin/withdraw/approve`
**Purpose**: Approve withdrawal
**Auth**: Admin Required
**Input**: `{"withdrawal_id": "number"}`

#### POST `/admin/withdraw/reject`
**Purpose**: Reject withdrawal
**Auth**: Admin Required
**Input**: `{"withdrawal_id": "number"}`

#### POST `/admin/user/ban`
**Purpose**: Ban user
**Auth**: Admin Required
**Input**: `{"user_id": "number"}`

#### POST `/admin/user/freeze`
**Purpose**: Suspend user
**Auth**: Admin Required
**Input**: `{"user_id": "number"}`

#### GET `/admin/referrals`
**Purpose**: All referral data
**Auth**: Admin Required
**Output**: Users with referral info

### Ads Routes (`routes/ads.py`)

#### POST `/ads/watch-ad`
**Purpose**: Watch ad and earn reward
**Auth**: JWT Required
**Output**: Success message

#### GET `/ads/ad-status`
**Purpose**: Check if user can watch ad today
**Auth**: JWT Required
**Output**: `{"can_watch": boolean}`

## 🔧 Services (Business Logic)

### 1. Deposit Service (`services/deposit.py`)
- **approve_deposit()**: Approve deposit, credit wallet, calculate commissions, apply rank rewards

### 2. Withdrawal Service (`services/withdrawal.py`)
- **request_withdrawal()**: Add withdrawal to queue
- **process_withdrawal()**: Process withdrawal from queue

### 3. Ads Service (`services/ads.py`)
- **watch_ad()**: Handle daily ad watching
- **reset_daily_ads()**: Reset daily ad watches

### 4. Referral Service (`services/referral.py`)
- **build_referral_tree()**: Build 5-level referral tree
- **get_upline()**: Get upline users
- **calculate_team_commissions()**: Calculate and credit commissions
- **apply_rank_rewards()**: Apply rank-based rewards

### 5. Wallet Service (`services/wallet.py`)
- **update_wallet_balance()**: Update main balance
- **update_withdrawable_balance()**: Update withdrawable balance

## 🛡️ Middleware

### 1. JWT Required (`middleware/jwt_required.py`)
- **jwt_required_decorator**: Basic JWT authentication
- **role_required**: Role-based access control

### 2. Rate Limiting (`middleware/rate_limiting.py`)
- Default limits: 200/day, 50/hour

### 3. Logging (`middleware/logging.py`)
- Request/response logging with duration

### 4. Duplicate Protection (`middleware/duplicate_protection.py`)
- Prevents duplicate requests within 5 minutes

## 💰 Business Logic Flow

### Registration Process
1. User registers with referral code (optional)
2. Password hashed with bcrypt
3. Unique referral code generated
4. Wallet created with zero balance
5. Referral tree built if referred

### Deposit Process
1. User submits deposit with screenshot
2. Admin approves/rejects deposit
3. On approval:
   - Amount credited to user wallet
   - Commissions calculated for upline (5 levels)
   - Rank rewards applied to leaders

### Withdrawal Process
1. User requests withdrawal
2. Added to queue with position
3. Admin processes from queue
4. Amount debited from withdrawable balance

### Ad Watching
1. User can watch 1 ad per day
2. Earns $0.50 per ad
3. Amount credited to wallet
4. Daily reset mechanism

### Commission Structure
- **Level 1**: 10% of deposit
- **Level 2**: 5% of deposit
- **Level 3**: 3% of deposit
- **Level 4**: 2% of deposit
- **Level 5**: 1% of deposit

## ⚠️ Issues Found

### 1. Inconsistent Decorators
- `admin.py` mein mixed decorators use kiye gaye
- `@role_required('admin')` vs `@admin_required`

### 2. Missing Decorator Definition
- `@admin_required` decorator define nahi hai

### 3. Unused Imports
- `get_jwt_identity` import but not used in admin.py

### 4. Database Configuration Issue
- MySQL config app.py mein hai but SQLAlchemy URI missing

### 5. Missing Error Handling
- Some services mein proper validation missing

## 🚀 Features Implemented

✅ **User Management**
- Registration/Login
- JWT Authentication
- Role-based access

✅ **Wallet System**
- Balance tracking
- Withdrawable amount separation
- Transaction logging

✅ **MLM System**
- 5-level referral tree
- Commission calculation
- Rank rewards

✅ **Deposit/Withdrawal**
- Admin approval system
- Queue management
- Fee calculation

✅ **Ad System**
- Daily ad watching
- Reward system

✅ **Admin Panel**
- User management
- Transaction approval
- System monitoring

## 🔄 Missing Features

❌ **Database Migrations**
❌ **Email Notifications**
❌ **SMS Integration**
❌ **Payment Gateway Integration**
❌ **Advanced Analytics**
❌ **Backup System**
❌ **API Documentation (Swagger)**
❌ **Unit Tests**
❌ **Docker Configuration**
❌ **Production Deployment Config**

## 🏃‍♂️ How to Run

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup MySQL Database**:
   ```sql
   CREATE DATABASE dailywealth;
   ```

3. **Run Application**:
   ```bash
   python app.py
   ```

4. **Access API**:
   - Base URL: `http://localhost:5000`
   - Auth endpoints: `/auth/*`
   - User endpoints: `/user/*`
   - Admin endpoints: `/admin/*`
   - Ads endpoints: `/ads/*`

## 📊 Database Schema Summary

```
users (Main user table)
├── wallets (1:1 with users)
├── deposits (1:Many with users)
├── withdrawals (1:Many with users)
├── ads_watches (1:Many with users)
├── referral_trees (Many:Many relationship)
└── rank_rewards (Many:Many relationship)
```

Ye complete documentation hai aapki DailyWealth app ka. Isme saari details hain jo aapko study karne ke liye chahiye.