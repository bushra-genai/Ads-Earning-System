# DailyWealth App - Complete Workflow

## 🔄 System Workflow Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Layer    │    │  Admin Layer    │    │  System Layer   │
│                 │    │                 │    │                 │
│ • Registration  │    │ • User Mgmt     │    │ • Commissions   │
│ • Login         │    │ • Deposits      │    │ • Rank Rewards  │
│ • Deposits      │    │ • Withdrawals   │    │ • Ad Rewards    │
│ • Withdrawals   │    │ • User Control  │    │ • Queue Mgmt    │
│ • Ad Watching   │    │ • Referrals     │    │ • Logging       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 1️⃣ User Registration Workflow

```
START: User Registration
│
├─ Input: username, email, password, referral_code (optional)
│
├─ Validation:
│  ├─ Check email uniqueness
│  ├─ Hash password with bcrypt
│  └─ Generate unique referral_code
│
├─ Database Operations:
│  ├─ Create User record
│  ├─ Create Wallet (balance=0)
│  └─ Build Referral Tree (if referred)
│
└─ Response: Success + referral_code
```

## 2️⃣ User Login Workflow

```
START: User Login
│
├─ Input: email, password
│
├─ Validation:
│  ├─ Find user by email
│  └─ Verify password with bcrypt
│
├─ JWT Token Generation:
│  └─ Create access_token with user_id
│
└─ Response: JWT token
```

## 3️⃣ Deposit Workflow

```
START: User Deposit Request
│
├─ Input: amount, screenshot_url
│
├─ Create Deposit Record:
│  ├─ user_id, amount, screenshot_url
│  └─ status = 'pending'
│
├─ Admin Review:
│  ├─ Approve ──┐
│  └─ Reject ───┼─ END
│              │
├─ On Approval:│
│  ├─ Update deposit.status = 'approved'
│  ├─ Credit user wallet
│  ├─ Calculate 5-level commissions
│  ├─ Apply rank rewards
│  └─ Log transactions
│
└─ Response: Success/Error
```

### 3.1 Commission Calculation Sub-workflow

```
Deposit Approved ($100 example)
│
├─ Get User's Upline (5 levels)
│
├─ Level 1 (Direct Referrer): $100 × 10% = $10
├─ Level 2: $100 × 5% = $5
├─ Level 3: $100 × 3% = $3
├─ Level 4: $100 × 2% = $2
└─ Level 5: $100 × 1% = $1
│
└─ Credit each level's wallet
```

### 3.2 Rank Rewards Sub-workflow

```
For Each Upline Leader:
│
├─ Check Member's Deposit Amount
│
├─ Find Matching Reward Slab:
│  ├─ $0-999: No reward
│  ├─ $1000-4999: $50 reward
│  ├─ $5000-9999: $200 reward
│  ├─ $10000-24999: $500 reward
│  ├─ $25000-49999: $1000 reward
│  └─ $50000+: $2000 reward
│
├─ Create RankRewards record
└─ Credit leader's wallet
```

## 4️⃣ Withdrawal Workflow

```
START: User Withdrawal Request
│
├─ Input: amount_usd
│
├─ Calculations:
│  ├─ fee = amount_usd × 5%
│  ├─ net_amount = amount_usd - fee
│  └─ amount_pkr = net_amount × 280
│
├─ Queue Management:
│  ├─ Get next queue position
│  └─ Create Withdrawal record (status='queued')
│
├─ Admin Processing:
│  ├─ Approve ──┐
│  └─ Reject ───┼─ END
│              │
├─ On Approval:│
│  ├─ Debit withdrawable balance
│  ├─ Update status = 'approved'
│  └─ Log transaction
│
└─ Response: Success/Error
```

## 5️⃣ Ad Watching Workflow

```
START: User Watches Ad
│
├─ Check Daily Limit:
│  ├─ Already watched today? ──┐
│  └─ Can watch ──────────────┐ │
│                             │ │
├─ Create/Update AdsWatch:    │ │
│  ├─ user_id, date=today     │ │
│  ├─ watched = true          │ │
│  └─ earned_amount = $0.50   │ │
│                             │ │
├─ Credit Wallet:             │ │
│  └─ Add $0.50 to balance    │ │
│                             │ │
└─ Response: Success ─────────┘ │
                                │
   Response: Already watched ───┘
```

## 6️⃣ Admin Management Workflow

```
Admin Dashboard
│
├─ User Management:
│  ├─ List all users
│  ├─ Ban user (status='banned')
│  └─ Freeze user (status='suspended')
│
├─ Deposit Management:
│  ├─ View pending deposits
│  ├─ Approve deposit (trigger commissions)
│  └─ Reject deposit
│
├─ Withdrawal Management:
│  ├─ View queued withdrawals
│  ├─ Process withdrawal (debit balance)
│  └─ Reject withdrawal
│
└─ Referral Monitoring:
   └─ View all referral relationships
```

## 7️⃣ Database Transaction Flow

```
User Action ──┐
              │
              ├─ Begin Transaction
              │
              ├─ Validate Input
              │
              ├─ Update Database:
              │  ├─ Primary table
              │  ├─ Related tables
              │  └─ Wallet updates
              │
              ├─ Calculate Effects:
              │  ├─ Commissions
              │  ├─ Rank rewards
              │  └─ Queue positions
              │
              ├─ Commit Transaction
              │
              └─ Log Activity
```

## 8️⃣ Security & Middleware Flow

```
API Request
│
├─ Rate Limiting Check (50/hour, 200/day)
│
├─ Duplicate Protection (5-min cache)
│
├─ JWT Authentication:
│  ├─ Token validation
│  └─ Extract user_id
│
├─ Role Authorization:
│  ├─ Admin routes: Check role='admin'
│  └─ User routes: Valid user
│
├─ Request Logging
│
├─ Execute Business Logic
│
├─ Response Logging
│
└─ Return Response
```

## 9️⃣ MLM Tree Structure Flow

```
Registration with Referral Code
│
├─ Find Referrer by referral_code
│
├─ Set referred_by = referrer.id
│
├─ Build Referral Tree:
│  │
│  ├─ Level 1: Direct referrer
│  ├─ Level 2: Referrer's referrer
│  ├─ Level 3: Level 2's referrer
│  ├─ Level 4: Level 3's referrer
│  └─ Level 5: Level 4's referrer
│
└─ Store in ReferralTree table
```

## 🔟 Error Handling Flow

```
Any Operation
│
├─ Try Block:
│  ├─ Begin database transaction
│  ├─ Execute business logic
│  └─ Commit transaction
│
├─ Catch Exception:
│  ├─ Rollback transaction
│  ├─ Log error details
│  └─ Return error response
│
└─ Finally:
   └─ Close database connections
```

## 📊 Data Flow Summary

```
User Input ──┐
             │
             ├─ Validation Layer
             │
             ├─ Authentication Layer
             │
             ├─ Business Logic Layer:
             │  ├─ Services (deposit, withdrawal, ads, referral)
             │  └─ Wallet operations
             │
             ├─ Database Layer:
             │  ├─ Models (User, Wallet, Deposit, etc.)
             │  └─ Transactions
             │
             └─ Response Layer
```

## 🎯 Key Business Rules

### Commission Rules:
- **5 levels deep** maximum
- **Percentages**: 10%, 5%, 3%, 2%, 1%
- **Triggered on**: Deposit approval only

### Rank Reward Rules:
- **Based on**: Individual member deposits
- **Applied to**: All upline leaders
- **One-time**: Per member per deposit

### Ad Watching Rules:
- **Limit**: 1 ad per day per user
- **Reward**: $0.50 per ad
- **Reset**: Daily at midnight

### Withdrawal Rules:
- **Fee**: 5% of withdrawal amount
- **Queue**: FIFO (First In, First Out)
- **Currency**: USD to PKR conversion

## 🔄 Daily Automated Tasks

```
Scheduler (APScheduler)
│
├─ Daily Reset:
│  └─ Reset ad watching status
│
├─ Queue Processing:
│  └─ Process pending withdrawals
│
└─ Maintenance:
   ├─ Clean old logs
   └─ Update exchange rates
```

This workflow covers all major processes in your DailyWealth MLM application! 🚀