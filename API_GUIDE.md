# 📖 Digital Wallet API Guide

Panduan lengkap untuk menggunakan Digital Wallet API.

## Base URL

```
http://localhost:5000/api
```

## Authentication

Semua endpoint (kecuali login dan register) memerlukan JWT token di header:

```
Authorization: Bearer <your-jwt-token>
```

---

## 1. Authentication Endpoints

### Login

Mendapatkan JWT token untuk akses API.

**Endpoint:** `POST /api/auth/login`

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

**Response Success (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "081234567890"
  }
}
```

**Response Error (401):**
```json
{
  "error": "Invalid credentials"
}
```

### Register

Registrasi user baru.

**Endpoint:** `POST /api/auth/register`

**Request Body:**
```json
{
  "name": "New User",
  "email": "newuser@example.com",
  "phone": "081234567899",
  "password": "password123"
}
```

**Response Success (201):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 4,
    "name": "New User",
    "email": "newuser@example.com",
    "phone": "081234567899"
  }
}
```

**Response Error (400):**
```json
{
  "error": "Email already registered"
}
```

---

## 2. User Management

### Get All Users

**Endpoint:** `GET /api/users`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "users": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "081234567890"
    },
    {
      "id": 2,
      "name": "Jane Smith",
      "email": "jane@example.com",
      "phone": "081234567891"
    }
  ]
}
```

### Get User by ID

**Endpoint:** `GET /api/users/:id`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "081234567890"
  }
}
```

### Update User

**Endpoint:** `PUT /api/users/:id`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "John Doe Updated",
  "phone": "081234567890"
}
```

**Response (200):**
```json
{
  "user": {
    "id": 1,
    "name": "John Doe Updated",
    "email": "john@example.com",
    "phone": "081234567890"
  }
}
```

**Note:** User hanya bisa update data dirinya sendiri.

### Verify Token

**Endpoint:** `GET /api/users/verify`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "081234567890"
  }
}
```

---

## 3. Wallet Management

### Get User Wallets

**Endpoint:** `GET /api/wallets`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "wallets": [
    {
      "id": 1,
      "user_id": 1,
      "balance": 1000000,
      "currency": "IDR",
      "status": "active"
    }
  ]
}
```

### Get Wallet by ID

**Endpoint:** `GET /api/wallets/:id`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "wallet": {
    "id": 1,
    "user_id": 1,
    "balance": 1000000,
    "currency": "IDR",
    "status": "active"
  }
}
```

### Get Wallet Balance

**Endpoint:** `GET /api/wallets/:id/balance`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "wallet_id": 1,
  "balance": 1000000,
  "currency": "IDR"
}
```

### Top Up Wallet

**Endpoint:** `POST /api/wallets/:id/topup`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "amount": 100000
}
```

**Response (200):**
```json
{
  "message": "Top up successful",
  "wallet": {
    "id": 1,
    "user_id": 1,
    "balance": 1100000,
    "currency": "IDR",
    "status": "active"
  }
}
```

**Validasi:**
- Amount harus > 0
- Amount dalam format integer (tanpa desimal)

---

## 4. Transaction Management

### Get All Transactions

**Endpoint:** `GET /api/transactions`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "transactions": [
    {
      "id": 3,
      "user_id": 1,
      "wallet_id": 1,
      "type": "payment",
      "amount": 50000,
      "description": "Payment for service",
      "status": "completed",
      "created_at": "2024-01-03T14:30:00"
    },
    {
      "id": 1,
      "user_id": 1,
      "wallet_id": 1,
      "type": "topup",
      "amount": 500000,
      "description": "Initial top up",
      "status": "completed",
      "created_at": "2024-01-01T10:00:00"
    }
  ]
}
```

**Transaction Types:**
- `topup`: Top up saldo
- `payment`: Pembayaran ke merchant
- `transfer`: Transfer ke user lain
- `withdrawal`: Penarikan saldo

### Get Transaction by ID

**Endpoint:** `GET /api/transactions/:id`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "transaction": {
    "id": 1,
    "user_id": 1,
    "wallet_id": 1,
    "type": "topup",
    "amount": 500000,
    "description": "Initial top up",
    "status": "completed",
    "created_at": "2024-01-01T10:00:00"
  }
}
```

### Get Transactions by Wallet

**Endpoint:** `GET /api/transactions/wallet/:wallet_id`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "transactions": [
    {
      "id": 1,
      "user_id": 1,
      "wallet_id": 1,
      "type": "topup",
      "amount": 500000,
      "description": "Initial top up",
      "status": "completed",
      "created_at": "2024-01-01T10:00:00"
    }
  ]
}
```

### Get Transaction Statistics

**Endpoint:** `GET /api/transactions/stats`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "total_transactions": 5,
  "total_topup": 1000000,
  "total_payment": 250000,
  "total_transfer": 0,
  "net_amount": 750000
}
```

---

## 5. Payment Processing

### Get All Payments

**Endpoint:** `GET /api/payments`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "payments": [
    {
      "id": 1,
      "user_id": 1,
      "wallet_id": 1,
      "merchant": "Tokopedia",
      "amount": 50000,
      "status": "completed",
      "payment_method": "wallet",
      "created_at": "2024-01-03T14:30:00"
    }
  ]
}
```

### Get Payment by ID

**Endpoint:** `GET /api/payments/:id`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "payment": {
    "id": 1,
    "user_id": 1,
    "wallet_id": 1,
    "merchant": "Tokopedia",
    "amount": 50000,
    "status": "completed",
    "payment_method": "wallet",
    "created_at": "2024-01-03T14:30:00"
  }
}
```

### Process Payment

**Endpoint:** `POST /api/payments/pay`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "wallet_id": 1,
  "merchant": "Tokopedia",
  "amount": 50000
}
```

**Response (201):**
```json
{
  "message": "Payment successful",
  "payment": {
    "id": 2,
    "user_id": 1,
    "wallet_id": 1,
    "merchant": "Tokopedia",
    "amount": 50000,
    "status": "completed",
    "payment_method": "wallet",
    "created_at": "2024-01-05T10:15:00"
  }
}
```

**Validasi:**
- Wallet harus milik user yang login
- Saldo harus cukup
- Amount harus > 0

### Process Transfer

**Endpoint:** `POST /api/payments/transfer`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "from_wallet_id": 1,
  "to_user_id": 2,
  "amount": 25000
}
```

**Response (201):**
```json
{
  "message": "Transfer successful",
  "from_wallet_id": 1,
  "to_wallet_id": 2,
  "amount": 25000
}
```

**Validasi:**
- Source wallet harus milik user yang login
- Destination user harus ada
- Saldo harus cukup
- Amount harus > 0

---

## 6. Error Responses

### 400 Bad Request
```json
{
  "error": "Missing required fields"
}
```

### 401 Unauthorized
```json
{
  "error": "Token is missing"
}
```
atau
```json
{
  "error": "Invalid token"
}
```
atau
```json
{
  "error": "Token has expired"
}
```

### 403 Forbidden
```json
{
  "error": "Unauthorized to access this resource"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

### 503 Service Unavailable
```json
{
  "error": "Service unavailable",
  "message": "Could not connect to the service"
}
```

### 504 Gateway Timeout
```json
{
  "error": "Request timeout",
  "message": "Service did not respond within 5 seconds"
}
```

---

## 7. Testing Flow Examples

### Scenario 1: New User Registration & Top Up

```bash
# 1. Register
POST /api/auth/register
{
  "name": "Test User",
  "email": "test@example.com",
  "phone": "081234567899",
  "password": "password123"
}
# Save token from response

# 2. Get Wallets (should be empty)
GET /api/wallets
Authorization: Bearer <token>

# 3. Create Wallet
POST /api/wallets
Authorization: Bearer <token>

# 4. Top Up
POST /api/wallets/1/topup
Authorization: Bearer <token>
{
  "amount": 500000
}

# 5. Check Balance
GET /api/wallets/1/balance
Authorization: Bearer <token>
```

### Scenario 2: Make Payment

```bash
# 1. Login
POST /api/auth/login
{
  "email": "john@example.com",
  "password": "password123"
}

# 2. Check Balance
GET /api/wallets/1/balance
Authorization: Bearer <token>

# 3. Make Payment
POST /api/payments/pay
Authorization: Bearer <token>
{
  "wallet_id": 1,
  "merchant": "Shopee",
  "amount": 100000
}

# 4. Check Transaction History
GET /api/transactions
Authorization: Bearer <token>

# 5. Check Updated Balance
GET /api/wallets/1/balance
Authorization: Bearer <token>
```

### Scenario 3: Transfer Between Users

```bash
# User A (john@example.com)
# 1. Login as User A
POST /api/auth/login
{
  "email": "john@example.com",
  "password": "password123"
}

# 2. Transfer to User B
POST /api/payments/transfer
Authorization: Bearer <token_user_a>
{
  "from_wallet_id": 1,
  "to_user_id": 2,
  "amount": 50000
}

# User B (jane@example.com)
# 3. Login as User B
POST /api/auth/login
{
  "email": "jane@example.com",
  "password": "password123"
}

# 4. Check balance received
GET /api/wallets
Authorization: Bearer <token_user_b>
```

---

## 8. Rate Limiting & Timeouts

### Request Timeout
- Default: 5 seconds
- Berlaku untuk semua inter-service communication
- Dapat dikonfigurasi via environment variable `REQUEST_TIMEOUT`

### Token Expiration
- JWT token valid selama 24 jam
- Setelah expired, user harus login ulang

---

## 9. Best Practices

### Security
1. Selalu simpan token dengan aman
2. Jangan share token ke pihak lain
3. Logout dan hapus token saat selesai
4. Gunakan HTTPS di production

### Performance
1. Cache token untuk mengurangi login request
2. Batch multiple GET requests jika memungkinkan
3. Gunakan pagination untuk data yang besar

### Error Handling
1. Selalu check response status code
2. Handle semua possible error responses
3. Implement retry logic untuk timeout errors
4. Log errors untuk debugging

---

## 10. Troubleshooting

### Token Invalid/Expired
**Solution:** Login ulang untuk mendapatkan token baru

### Request Timeout (504)
**Solution:** 
- Check service health: `GET /health`
- Retry request
- Contact admin jika masalah persisten

### Insufficient Balance (400)
**Solution:** Top up wallet sebelum melakukan payment/transfer

### Service Unavailable (503)
**Solution:**
- Check service health
- Tunggu beberapa saat dan retry
- Contact admin jika service down

---

## Support

Untuk pertanyaan atau issue, hubungi:
- Email: support@digitalwallet.com
- API Status: http://localhost:5000/health
