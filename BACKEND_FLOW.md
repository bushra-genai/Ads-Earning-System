# Backend Flow Diagrams - Daily Wealth System

## 1. Overall Architecture Flow

```mermaid
graph TB
    Client[Client/Postman] -->|HTTP Request| Flask[Flask App]
    Flask -->|Route| Auth[routes/auth.py]
    Flask -->|Route| User[routes/user.py]
    Flask -->|Route| Admin[routes/admin.py]
    Flask -->|Route| Ads[routes/ads.py]
    Flask -->|Route| Plan[routes/plan.py]
    
    Auth -->|Business Logic| AuthService[No Service]
    User -->|Business Logic| Services[services/]
    Admin -->|Business Logic| Services
    Ads -->|Business Logic| AdsService[services/ads.py]
    Plan -->|Business Logic| PlanService[services/plan.py]
    
    Services -->|Query/Update| DB[(MySQL Database)]
    AdsService -->|Query/Update| DB
    PlanService -->|Query/Update| DB
    
    DB -->|Response| Services
    Services -->|JSON| Flask
    Flask -->|HTTP Response| Client
```

---

## 2. Request Processing Flow

```mermaid
sequenceDiagram
    participant Client
    participant Flask
    participant Middleware
    participant Route
    participant Service
    participant Database
    
    Client->>Flask: HTTP Request
    Flask->>Middleware: @jwt_required()
    Middleware->>Middleware: Verify JWT Token
    Middleware->>Route: Allow/Deny
    Route->>Service: Call business logic
    Service->>Database: SQL Query
    Database-->>Service: Data
    Service-->>Route: Processed data
    Route-->>Flask: JSON response
    Flask-->>Client: HTTP Response
```

---

## 3. User Registration Flow

```mermaid
graph LR
    A[POST /auth/register] --> B{Validate Input}
    B -->|Invalid| C[Return 400 Error]
    B -->|Valid| D[Check Username Exists]
    D -->|Exists| E[Return 400 Error]
    D -->|New| F[Hash Password]
    F --> G[Generate Referral Code]
    G --> H[Create User Record]
    H --> I[Create Wallet Record]
    I --> J[Return 201 Success]
```

---

## 4. Plan Purchase & Activation Flow

```mermaid
graph TB
    Start[User: POST /plan/buy] --> ValidatePlan{Plan Valid?}
    ValidatePlan -->|No| Error1[400 Error]
    ValidatePlan -->|Yes| CheckActive{Has Active Plan?}
    CheckActive -->|Yes| Error2[400 Error]
    CheckActive -->|No| CreateDeposit[Create Deposit<br/>type=plan_purchase<br/>status=pending]
    CreateDeposit --> UpdateUser[User:<br/>plan_status=pending<br/>active_plan=starter]
    UpdateUser --> WaitAdmin[Wait for Admin]
    
    WaitAdmin --> Admin[Admin: POST /deposit/approve]
    Admin --> CheckType{Deposit Type?}
    CheckType -->|plan_purchase| ActivatePlan[Activate Plan:<br/>plan_status=active<br/>ads_permission=true<br/>daily_ads_limit=10]
    CheckType -->|regular| CreditWallet[Credit Wallet & Withdrawable]
    
    ActivatePlan --> Done[✅ User Can Watch Ads]
    CreditWallet --> Done2[✅ User Can Withdraw]
```

---

## 5. Admin Plan Management Flow

```mermaid
graph TB
    Admin[Admin] -->|Include Inactive?| List[GET /admin/plans]
    List --> DB[(Database)]
    DB -->|List of Plans| Admin
    
    Admin -->|New Plan Data| Create[POST /admin/plans]
    Create -->|Validate Slug| CheckSlug{Slug Exists?}
    CheckSlug -->|Yes| Error[400 Error]
    CheckSlug -->|No| Insert[Insert into DB]
    Insert --> Success[201 Created]
    
    Admin -->|Update Data| Update[PUT /admin/plans/:id]
    Update --> Modify[Modify Plan Fields]
    Modify --> Save[Save to DB]
    
    Admin -->|Delete| Delete[DELETE /admin/plans/:id]
    Delete --> Soft{Hard Delete?}
    Soft -->|No| Deactivate[Set is_active=False]
    Soft -->|Yes| Remove[Remove from DB]
```

---

## 6. Ad Watching Flow

```mermaid
graph TB
    Request[POST /ads/watch-ad] --> Auth{JWT Valid?}
    Auth -->|No| E1[401 Error]
    Auth -->|Yes| PlanCheck{Has Active Plan?}
    PlanCheck -->|No| E2[403 Plan Required]
    PlanCheck -->|Yes| GetRecord[Get Today's AdsWatch]
    GetRecord --> CheckLimit{ads_watched < daily_ads_limit?}
    CheckLimit -->|No| E3[400 Daily Limit Reached]
    CheckLimit -->|Yes| Increment[ads_watched += 1<br/>earned_amount += 0.50]
    Increment --> CreditWallet[Wallet:<br/>balance += 0.50<br/>withdrawable += 0.50]
    CreditWallet --> Commit[db.session.commit]
    Commit --> Success[200 Success]
```

---

## 7. Withdrawal Flow

```mermaid
graph TB
    Request[POST /user/withdraw] --> CheckDaily{Daily Requests < 3?}
    CheckDaily -->|No| E1[400 Daily Limit]
    CheckDaily -->|Yes| CheckAmount{Amount <= 500 PKR?}
    CheckAmount -->|No| E2[400 Amount Limit]
    CheckAmount -->|Yes| CreateWithdrawal[Create Withdrawal<br/>status=queued<br/>queue_position=N]
    CreateWithdrawal --> WaitAdmin[Wait for Admin]
    
    WaitAdmin --> Admin[Admin: POST /withdraw/approve]
    Admin --> CheckBalance{User Balance >= Amount?}
    CheckBalance -->|No| E3[400 Insufficient Balance]
    CheckBalance -->|Yes| Deduct[Deduct from Wallet:<br/>balance -= amount<br/>withdrawable -= amount]
    Deduct --> UpdateStatus[status = approved]
    UpdateStatus --> Success[200 Success]
```

---

## 8. Deposit & Commission Flow

```mermaid
graph TB
    User[User: POST /deposit] --> CreateDeposit[Create Deposit<br/>type=regular<br/>status=pending]
    CreateDeposit --> Admin[Admin: Approve]
    Admin --> CreditUser[Credit User Wallet]
    CreditUser --> GetUpline[Get Upline Chain<br/>5 Levels]
    GetUpline --> Level1[Level 1: 10% Commission]
    Level1 --> Level2[Level 2: 5% Commission]
    Level2 --> Level3[Level 3: 3% Commission]
    Level3 --> Level4[Level 4: 2% Commission]
    Level4 --> Level5[Level 5: 1% Commission]
    Level5 --> RankCheck[Check Rank Rewards]
    RankCheck --> Done[✅ Complete]
```

---

## 9. Daily Ad Reset Mechanism

```mermaid
graph LR
    A[12:00 AM] --> B[New Date]
    B --> C[AdsWatch uses date as PK]
    C --> D[Old date records remain]
    D --> E[New date = New record]
    E --> F[ads_watched starts at 0]
```

---

## 10. Database Schema Relationships

```mermaid
erDiagram
    USERS ||--o{ WALLETS : has
    USERS ||--o{ DEPOSITS : makes
    USERS ||--o{ WITHDRAWALS : requests
    USERS ||--o{ ADS_WATCH : watches
    USERS ||--o{ USERS : refers
    
    USERS {
        int id PK
        string username
        string email
        string referral_code
        int referred_by FK
        string active_plan
        string plan_status
        int daily_ads_limit
    }
    
    WALLETS {
        int user_id PK
        float balance
        float withdrawable
        float total_earned
    }
    
    DEPOSITS {
        int id PK
        int user_id FK
        float amount
        string deposit_type
        string plan_name
        string status
    }
    
    WITHDRAWALS {
        int id PK
        int user_id FK
        float amount_usd
        float amount_pkr
        string status
        int queue_position
    }
    
    ADS_WATCH {
        int user_id PK
        date date PK
        int ads_watched
        float earned_amount
    }
```

---

## 11. Complete User Journey Flow

```mermaid
graph TB
    Start([New User]) --> Register[Register Account]
    Register --> Login1[Login]
    Login1 --> ViewPlans[View Plans]
    ViewPlans --> BuyPlan[Buy Starter Plan]
    BuyPlan --> Wait1[Wait Admin Approval]
    Wait1 --> PlanActive{Plan Active?}
    PlanActive --> WatchAds[Watch 10 Ads<br/>Earn $5]
    WatchAds --> CheckWallet[Check Wallet<br/>$5 Available]
    CheckWallet --> Withdraw[Request Withdrawal<br/>$3]
    Withdraw --> Wait2[Wait Admin Approval]
    Wait2 --> Money([Receive Money 💰])
```

---

## File Structure

```
Dailywealthby-sajid-main/
├── app.py                 # Main Flask application
├── config.py             # Configuration (Plans, Limits, etc.)
├── models/
│   ├── user.py           # User model
│   ├── wallet.py         # Wallet model
│   ├── deposit.py        # Deposit model
│   ├── withdrawal.py     # Withdrawal model
│   ├── ads_watch.py      # AdsWatch model
│   └── plan.py           # Plan model (Dynamic Plans)
├── routes/
│   ├── auth.py           # Auth routes
│   ├── user.py           # User routes (deposit, withdraw, wallet)
│   ├── admin.py          # Admin routes
│   ├── ads.py            # Ad watching routes
│   └── plan.py           # Plan purchase routes
├── services/
│   ├── ads.py            # Ad watching logic
│   ├── plan.py           # Plan activation logic
│   ├── plan_admin.py     # Plan CRUD logic
│   ├── deposit.py        # Deposit approval logic
│   ├── withdrawal.py     # Withdrawal processing
│   ├── wallet.py         # Wallet operations
│   └── referral.py       # Commission calculations
└── middleware/
    ├── jwt_required.py   # JWT & Plan decorators
    ├── logging.py        # Request logging
    └── rate_limiting.py  # Rate limiting
```
