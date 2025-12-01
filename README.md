# 💳 Digital Wallet - Microservices Architecture

Sistem Digital Wallet berbasis microservices dengan Python Flask, JWT Authentication, API Gateway, dan Request Timeout.

## 📋 Daftar Isi

- [Arsitektur Sistem](#arsitektur-sistem)
- [Fitur Utama](#fitur-utama)
- [Teknologi yang Digunakan](#teknologi-yang-digunakan)
- [Microservices](#microservices)
- [Instalasi](#instalasi)
- [Cara Menjalankan](#cara-menjalankan)
- [API Documentation](#api-documentation)
- [Testing dengan Postman](#testing-dengan-postman)
- [Struktur Project](#struktur-project)

---

## 🏗️ Arsitektur Sistem

```
┌─────────────┐
│   Frontend  │ (Vue.js)
│  (Browser)  │
└──────┬──────┘
       │
       ↓ HTTP/REST
┌──────────────────┐
│   API Gateway    │ (Port 5000)
│  Request Timeout │
└────────┬─────────┘
         │
    ┌────┴────┬────────┬─────────┐
    ↓         ↓        ↓         ↓
┌────────┐ ┌────────┐ ┌───────┐ ┌─────────┐
│  User  │ │ Wallet │ │ Trans │ │ Payment │
│Service │ │Service │ │Service│ │ Service │
│  5001  │ │  5002  │ │  5003 │ │  5004   │
└────────┘ └────────┘ └───────┘ └─────────┘
```

### Komunikasi Antar Service

- **Frontend → API Gateway**: REST API calls dengan JWT Token
- **API Gateway → Services**: HTTP requests dengan timeout protection
- **Service → Service**: Internal API calls (e.g., Wallet ↔ User, Payment ↔ Transaction)

---

## ✨ Fitur Utama

### 1. **Authentication & Authorization**
   - ✅ JWT Token-based authentication
   - ✅ Token expiration (24 hours)
   - ✅ Protected endpoints
   - ✅ User registration & login

### 2. **User Management Service**
   - ✅ User CRUD operations
   - ✅ Profile management
   - ✅ Token verification

### 3. **Wallet Service**
   - ✅ Create wallet
   - ✅ View balance
   - ✅ Top up wallet
   - ✅ Deduct balance

### 4. **Transaction Service**
   - ✅ Transaction history
   - ✅ Transaction by wallet
   - ✅ Transaction statistics
   - ✅ Multiple transaction types (topup, payment, transfer)

### 5. **Payment Service**
   - ✅ Payment to merchants
   - ✅ Transfer between users
   - ✅ Automatic transaction recording
   - ✅ Balance validation

### 6. **API Gateway**
   - ✅ Single entry point
   - ✅ Request timeout (5 seconds default)
   - ✅ Service health monitoring
   - ✅ Error handling

---

## 🛠️ Teknologi yang Digunakan

### Backend
- **Python 3.11**: Programming language
- **Flask**: Web framework
- **PyJWT**: JWT authentication
- **Flask-CORS**: Cross-Origin Resource Sharing
- **Requests**: HTTP library for inter-service communication

### Frontend
- **Vue.js 3**: Progressive JavaScript framework
- **Axios**: HTTP client
- **CSS3**: Styling dengan gradient dan animations

### DevOps
- **Docker & Docker Compose**: Containerization
- **Bash Scripts**: Automation

---

## 📦 Microservices

### 1. User Service (Port 5001)

**Provider API untuk manajemen user**

Endpoints:
- `POST /auth/login` - Login dan dapatkan JWT token
- `POST /auth/register` - Registrasi user baru
- `GET /users` - List semua users (protected)
- `GET /users/:id` - Detail user (protected)
- `PUT /users/:id` - Update user (protected)
- `DELETE /users/:id` - Delete user (protected)
- `GET /users/verify` - Verifikasi token (protected)

### 2. Wallet Service (Port 5002)

**Provider API untuk manajemen wallet dan saldo**

Endpoints:
- `GET /wallets` - List wallet user (protected)
- `GET /wallets/:id` - Detail wallet (protected)
- `POST /wallets` - Create wallet baru (protected)
- `GET /wallets/:id/balance` - Cek saldo (protected)
- `POST /wallets/:id/topup` - Top up saldo (protected)
- `POST /wallets/:id/deduct` - Deduct saldo (protected, internal)

**Konsumsi API:**
- Memanggil User Service untuk verifikasi user

### 3. Transaction Service (Port 5003)

**Provider API untuk riwayat transaksi**

Endpoints:
- `GET /transactions` - List transaksi user (protected)
- `GET /transactions/:id` - Detail transaksi (protected)
- `POST /transactions` - Create transaksi (protected)
- `GET /transactions/wallet/:id` - Transaksi by wallet (protected)
- `GET /transactions/stats` - Statistik transaksi (protected)

**Konsumsi API:**
- Memanggil Wallet Service untuk validasi wallet

### 4. Payment Service (Port 5004)

**Provider API untuk proses pembayaran**

Endpoints:
- `GET /payments` - List pembayaran (protected)
- `GET /payments/:id` - Detail pembayaran (protected)
- `POST /payments/pay` - Bayar ke merchant (protected)
- `POST /payments/transfer` - Transfer ke user lain (protected)

**Konsumsi API:**
- Memanggil Wallet Service untuk deduct/topup saldo
- Memanggil Transaction Service untuk catat transaksi

### 5. API Gateway (Port 5000)

**Central entry point dengan request timeout**

Features:
- Route semua requests ke services yang sesuai
- Request timeout protection (default 5 detik)
- Health check monitoring
- Error handling

---

## 📥 Instalasi

### Prerequisites

- Python 3.11+
- pip
- Git

### Clone Repository

```bash
git clone <repository-url>
cd digital-wallet
```

### Install Dependencies

```bash
pip install -r requirements.txt --break-system-packages
```

---

## 🚀 Cara Menjalankan

### Opsi 1: Menjalankan Secara Manual

#### 1. Start User Service
```bash
cd user-service
python app.py
# Running on http://localhost:5001
```

#### 2. Start Wallet Service
```bash
cd wallet-service
python app.py
# Running on http://localhost:5002
```

#### 3. Start Transaction Service
```bash
cd transaction-service
python app.py
# Running on http://localhost:5003
```

#### 4. Start Payment Service
```bash
cd payment-service
python app.py
# Running on http://localhost:5004
```

#### 5. Start API Gateway
```bash
cd api-gateway
python app.py
# Running on http://localhost:5000
```

#### 6. Open Frontend
```bash
# Buka file frontend/index.html di browser
# Atau gunakan simple HTTP server
cd frontend
python -m http.server 8080
# Buka http://localhost:8080
```

### Opsi 2: Menggunakan Bash Script

```bash
chmod +x start-services.sh
./start-services.sh
```

Script akan:
- Install dependencies
- Start semua services secara otomatis
- Menampilkan status dan port masing-masing service
- Press Ctrl+C untuk stop semua services

### Opsi 3: Menggunakan Docker Compose

```bash
# Build dan start semua services
docker-compose up --build

# Stop services
docker-compose down
```

---

## 📚 API Documentation

### Authentication

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "password123"
}

Response:
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

#### Register
```http
POST /api/auth/register
Content-Type: application/json

{
  "name": "New User",
  "email": "newuser@example.com",
  "phone": "081234567899",
  "password": "password123"
}
```

### Wallet Operations

#### Get Wallets
```http
GET /api/wallets
Authorization: Bearer <token>

Response:
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

#### Top Up Wallet
```http
POST /api/wallets/1/topup
Authorization: Bearer <token>
Content-Type: application/json

{
  "amount": 100000
}

Response:
{
  "message": "Top up successful",
  "wallet": {
    "id": 1,
    "balance": 1100000
  }
}
```

### Transactions

#### Get Transactions
```http
GET /api/transactions
Authorization: Bearer <token>

Response:
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

#### Get Transaction Statistics
```http
GET /api/transactions/stats
Authorization: Bearer <token>

Response:
{
  "total_transactions": 5,
  "total_topup": 1000000,
  "total_payment": 250000,
  "total_transfer": 0,
  "net_amount": 750000
}
```

### Payments

#### Process Payment
```http
POST /api/payments/pay
Authorization: Bearer <token>
Content-Type: application/json

{
  "wallet_id": 1,
  "merchant": "Tokopedia",
  "amount": 50000
}

Response:
{
  "message": "Payment successful",
  "payment": {
    "id": 2,
    "merchant": "Tokopedia",
    "amount": 50000,
    "status": "completed"
  }
}
```

#### Process Transfer
```http
POST /api/payments/transfer
Authorization: Bearer <token>
Content-Type: application/json

{
  "from_wallet_id": 1,
  "to_user_id": 2,
  "amount": 25000
}

Response:
{
  "message": "Transfer successful",
  "from_wallet_id": 1,
  "to_wallet_id": 2,
  "amount": 25000
}
```

### Health Check

```http
GET /health

Response:
{
  "service": "api-gateway",
  "status": "healthy",
  "services": {
    "user-service": "healthy",
    "wallet-service": "healthy",
    "transaction-service": "healthy",
    "payment-service": "healthy"
  }
}
```

---

## 🧪 Testing dengan Postman

### Import Collection

1. Buka Postman
2. Click Import → Upload file `Digital-Wallet-API.postman_collection.json`
3. Collection akan muncul di sidebar

### Setup Environment Variables

Di Postman, buat environment baru dengan variables:

```
base_url: http://localhost:5000/api
token: (akan terisi setelah login)
user_id: 1
wallet_id: 1
```

### Testing Flow

#### 1. Login
- Run request "Authentication → Login"
- Copy token dari response
- Set ke environment variable `token`

#### 2. Get User Info
- Run "User Management → Get User by ID"
- Verifikasi data user

#### 3. Get Wallet
- Run "Wallet Management → Get User Wallets"
- Catat wallet_id

#### 4. Top Up
- Run "Wallet Management → Top Up Wallet"
- Check balance bertambah

#### 5. Make Payment
- Run "Payment Processing → Process Payment"
- Check balance berkurang

#### 6. Check Transactions
- Run "Transaction Management → Get All Transactions"
- Verifikasi riwayat transaksi

#### 7. Check Statistics
- Run "Transaction Management → Get Transaction Stats"
- Lihat summary transaksi

---

## 📁 Struktur Project

```
digital-wallet/
│
├── user-service/
│   └── app.py                 # User management service
│
├── wallet-service/
│   └── app.py                 # Wallet management service
│
├── transaction-service/
│   └── app.py                 # Transaction service
│
├── payment-service/
│   └── app.py                 # Payment processing service
│
├── api-gateway/
│   └── app.py                 # API Gateway with timeout
│
├── frontend/
│   └── index.html             # Vue.js frontend
│
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose setup
├── start-services.sh          # Bash script to start all services
├── Digital-Wallet-API.postman_collection.json
└── README.md                  # Documentation
```

---

## ⚙️ Konfigurasi

### Environment Variables

Setiap service dapat dikonfigurasi melalui environment variables:

```bash
# Common
SECRET_KEY=digital-wallet-secret-key-2024
REQUEST_TIMEOUT=5

# Service Ports
USER_SERVICE_PORT=5001
WALLET_SERVICE_PORT=5002
TRANSACTION_SERVICE_PORT=5003
PAYMENT_SERVICE_PORT=5004
GATEWAY_PORT=5000

# Service URLs (for inter-service communication)
USER_SERVICE_URL=http://localhost:5001
WALLET_SERVICE_URL=http://localhost:5002
TRANSACTION_SERVICE_URL=http://localhost:5003
PAYMENT_SERVICE_URL=http://localhost:5004
```

### Request Timeout

Default timeout untuk semua request antar service adalah **5 detik**.

Dapat diubah melalui environment variable:
```bash
export REQUEST_TIMEOUT=10  # 10 seconds
```

---

## 🔒 Security Features

1. **JWT Authentication**: Semua endpoint (kecuali login/register) memerlukan JWT token
2. **Token Expiration**: Token expire setelah 24 jam
3. **Authorization**: User hanya bisa akses data miliknya sendiri
4. **Request Timeout**: Mencegah long-running requests
5. **CORS Protection**: Konfigurasi CORS untuk frontend

---

## 🐛 Troubleshooting

### Service tidak bisa connect

**Problem**: `Service unavailable (503)`

**Solution**:
1. Pastikan semua services running
2. Check health endpoint: `GET /health`
3. Verifikasi port tidak digunakan aplikasi lain

### Request Timeout

**Problem**: `Request timeout (504)`

**Solution**:
1. Increase timeout di environment variable
2. Check apakah service yang dituju responsive
3. Monitor service logs

### Token Invalid

**Problem**: `Token is missing/invalid (401)`

**Solution**:
1. Login ulang untuk dapatkan token baru
2. Pastikan format: `Authorization: Bearer <token>`
3. Check token belum expired (24 jam)

### Insufficient Balance

**Problem**: `Insufficient balance (400)`

**Solution**:
1. Top up wallet terlebih dahulu
2. Check current balance via `/api/wallets/:id/balance`

---

## 📊 Data Demo

### Users
```
Email: john@example.com
Password: password123
Wallet Balance: Rp 1.000.000

Email: jane@example.com
Password: password123
Wallet Balance: Rp 500.000

Email: bob@example.com
Password: password123
Wallet Balance: Rp 750.000
```

---

## 🎯 Use Cases

### 1. Top Up E-Wallet
```
User → Login → Get Wallet → Top Up → Check Balance
```

### 2. Payment ke Merchant
```
User → Login → Get Wallet → Make Payment → Check Transaction History
```

### 3. Transfer ke User Lain
```
User A → Login → Get Wallet → Transfer to User B → Both Check Balance
```

### 4. View Transaction History
```
User → Login → Get Transactions → Filter by Wallet → View Stats
```

---

## 🚀 Future Enhancements

- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] Redis caching
- [ ] Message queue (RabbitMQ/Kafka)
- [ ] Advanced monitoring (Prometheus/Grafana)
- [ ] Rate limiting
- [ ] API versioning
- [ ] Webhook notifications
- [ ] Multi-currency support
- [ ] Transaction rollback mechanism
- [ ] Admin dashboard

---

## 📄 License

MIT License

---

## 👨‍💻 Developer

Created with ❤️ for Digital Wallet Microservices Project

**Contact:**
- Email: support@digitalwallet.com
- Documentation: http://localhost:5000/health

---

## 🙏 Acknowledgments

- Flask Framework
- Vue.js
- JWT.io
- Docker
- Postman

---

**Happy Coding! 🚀**
