from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import datetime
from functools import wraps
import os
import requests

app = Flask(__name__)
CORS(app)

SECRET_KEY = os.getenv('SECRET_KEY', 'digital-wallet-secret-key-2024')
TRANSACTION_SERVICE_URL = os.getenv("TRANSACTION_SERVICE_URL", "http://localhost:5003")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 5))
# ===== DUMMY DATABASE =====
wallets = {
    1: {"id": 1, "user_id": 1, "balance": 150000},
    2: {"id": 2, "user_id": 2, "balance": 300000},
}

transactions = [
    {"id": 1, "user_id": 1, "type": "topup", "amount": 150000, "created_at": "2024-12-01 10:00"},
    {"id": 2, "user_id": 1, "type": "payment", "amount": 50000, "created_at": "2024-12-02 12:30"},
]

# ===== TOKEN VALIDATION =====
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Token missing"}), 401

        try:
            token = token.replace("Bearer ", "")
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user_id = data["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(current_user_id, *args, **kwargs)
    return decorator

def record_transaction(user_id, wallet_id, txn_type, amount, description, token):
    """Kirim data transaksi ke transaction-service"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "wallet_id": wallet_id,
            "type": txn_type,
            "amount": amount,
            "description": description
        }
        response = requests.post(
            f"{TRANSACTION_SERVICE_URL}/transactions",
            json=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        if response.status_code == 201:
            return True
        print("Transaction service response:", response.text)
        return False
    except requests.RequestException as e:
        print("Error connecting to transaction service:", str(e))
        return False

# ===== AUTH =====
@app.route("/auth/login", methods=["POST"])
def login():
    email = request.json.get("email")
    password = request.json.get("password")

    if email != "john@example.com" or password != "password123":
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode(
        {"user_id": 1, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)},
        SECRET_KEY,
        algorithm="HS256"
    )

    return jsonify({
        "token": token,
        "user": {"id": 1, "name": "John Doe", "email": "john@example.com"}
    }), 200

# ===== WALLETS =====
@app.route("/wallets", methods=["GET"])
@token_required
def get_wallets(current_user_id):
    return jsonify({"wallets": list(wallets.values())}), 200

@app.route("/wallets/<int:wallet_id>", methods=["GET"])
@token_required
def get_wallet_by_id(current_user_id, wallet_id):
    wallet = wallets.get(wallet_id)
    if not wallet or wallet['user_id'] != current_user_id:
        return jsonify({"error": "Wallet not found"}), 404
    return jsonify({"wallet": wallet}), 200

@app.route("/wallets/user/<int:user_id>", methods=["GET"])
@token_required
def get_wallet_by_user(current_user_id, user_id):
    # Admins could get other user's wallet; here we only allow self
    if current_user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403
    user_wallets = [w for w in wallets.values() if w['user_id'] == user_id]
    if not user_wallets:
        return jsonify({"error": "No wallet found for user"}), 404
    # Assuming 1 wallet per user
    return jsonify({"wallet": user_wallets[0]}), 200

@app.route("/wallets/<int:wallet_id>/topup", methods=["POST"])
@token_required
def topup_wallet(current_user_id, wallet_id):
    wallet = wallets.get(wallet_id)
    if not wallet or wallet['user_id'] != current_user_id:
        return jsonify({"error": "Wallet not found"}), 404

    amount = request.json.get("amount", 0)
    if amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400

    wallet["balance"] += amount

    # Ambil token dari header untuk dikirim ke transaction-service
    token = request.headers.get("Authorization", "").replace("Bearer ", "")

    # Kirim transaksi ke transaction-service
    success = record_transaction(
        user_id=current_user_id,
        wallet_id=wallet_id,
        txn_type="topup",
        amount=amount,
        description="Topup wallet",
        token=token
    )

    if not success:
        return jsonify({"error": "Topup succeeded but failed to record in transaction service"}), 500

    return jsonify({"message": "Topup successful", "balance": wallet["balance"]}), 200

@app.route("/wallets/<int:wallet_id>/deduct", methods=["POST"])
@token_required
def deduct_wallet(current_user_id, wallet_id):
    wallet = wallets.get(wallet_id)
    if not wallet or wallet['user_id'] != current_user_id:
        return jsonify({"error": "Wallet not found"}), 404

    amount = request.json.get("amount", 0)
    if amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400

    if wallet["balance"] < amount:
        return jsonify({"error": "Insufficient balance"}), 400

    wallet["balance"] -= amount

    transactions.append({
        "id": len(transactions) + 1,
        "user_id": current_user_id,
        "type": "payment",
        "amount": amount,
        "created_at": str(datetime.datetime.now())
    })

    return jsonify({"message": "Deduct successful", "balance": wallet["balance"]}), 200

# ===== TRANSACTIONS =====
@app.route("/transactions", methods=["GET"])
@token_required
def get_transactions(current_user_id):
    return jsonify({"transactions": [t for t in transactions if t["user_id"] == current_user_id]}), 200

@app.route("/transactions/stats", methods=["GET"])
@token_required
def get_stats(current_user_id):
    total_topup = sum(t["amount"] for t in transactions if t["type"] == "topup")
    total_payment = sum(t["amount"] for t in transactions if t["type"] == "payment")

    return jsonify({
        "total_topup": total_topup,
        "total_payment": total_payment,
        "transaction_count": len(transactions),
    }), 200

# ===== HEALTH CHECK =====
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "wallet-service healthy"}), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5002))
    app.run(host="0.0.0.0", port=port, debug=True)
