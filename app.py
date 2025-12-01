from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import datetime
from functools import wraps
import os
import requests

app = Flask(__name__)
from flask_cors import CORS
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

SECRET_KEY = os.getenv('SECRET_KEY', 'digital-wallet-secret-key-2024')
USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://localhost:5001')
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 5))

# Database wallet (in-memory)
wallets_db = {
    1: {
        'id': 1,
        'user_id': 1,
        'balance': 1000000,
        'currency': 'IDR',
        'status': 'active'
    },
    2: {
        'id': 2,
        'user_id': 2,
        'balance': 500000,
        'currency': 'IDR',
        'status': 'active'
    },
    3: {
        'id': 3,
        'user_id': 3,
        'balance': 750000,
        'currency': 'IDR',
        'status': 'active'
    }
}

next_wallet_id = 4

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user_id, *args, **kwargs)
    
    return decorated

def verify_user_exists(user_id, token):
    """Verify user exists by calling user-service"""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(
            f'{USER_SERVICE_URL}/users/{user_id}',
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        return response.status_code == 200
    except requests.exceptions.Timeout:
        return False
    except requests.exceptions.RequestException:
        return False

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'service': 'wallet-service',
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat()
    })

@app.route('/wallets', methods=['GET'])
@token_required
def get_wallets(current_user_id):
    """Get all wallets for current user"""
    user_wallets = [w for w in wallets_db.values() if w['user_id'] == current_user_id]
    return jsonify({'wallets': user_wallets})

@app.route('/wallets/<int:wallet_id>', methods=['GET'])
@token_required
def get_wallet(current_user_id, wallet_id):
    """Get wallet by ID"""
    wallet = wallets_db.get(wallet_id)
    
    if not wallet:
        return jsonify({'error': 'Wallet not found'}), 404
    
    if wallet['user_id'] != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({'wallet': wallet})

@app.route('/wallets', methods=['POST'])
@token_required
def create_wallet(current_user_id):
    """Create new wallet"""
    global next_wallet_id
    
    # Verify user exists
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not verify_user_exists(current_user_id, token):
        return jsonify({'error': 'User verification failed'}), 400
    
    # Check if user already has a wallet
    for wallet in wallets_db.values():
        if wallet['user_id'] == current_user_id:
            return jsonify({'error': 'User already has a wallet'}), 400
    
    new_wallet = {
        'id': next_wallet_id,
        'user_id': current_user_id,
        'balance': 0,
        'currency': 'IDR',
        'status': 'active'
    }
    wallets_db[next_wallet_id] = new_wallet
    next_wallet_id += 1
    
    return jsonify({'wallet': new_wallet}), 201

@app.route('/wallets/<int:wallet_id>/balance', methods=['GET'])
@token_required
def get_balance(current_user_id, wallet_id):
    """Get wallet balance"""
    wallet = wallets_db.get(wallet_id)
    
    if not wallet:
        return jsonify({'error': 'Wallet not found'}), 404
    
    if wallet['user_id'] != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'wallet_id': wallet['id'],
        'balance': wallet['balance'],
        'currency': wallet['currency']
    })

@app.route('/wallets/<int:wallet_id>/topup', methods=['POST'])
@token_required
def topup_wallet(current_user_id, wallet_id):
    """Top up wallet balance"""
    wallet = wallets_db.get(wallet_id)
    
    if not wallet:
        return jsonify({'error': 'Wallet not found'}), 404
    
    if wallet['user_id'] != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    amount = data.get('amount', 0)
    
    if amount <= 0:
        return jsonify({'error': 'Invalid amount'}), 400
    
    wallet['balance'] += amount
    
    return jsonify({
        'message': 'Top up successful',
        'wallet': wallet
    })

@app.route('/wallets/<int:wallet_id>/deduct', methods=['POST'])
@token_required
def deduct_wallet(current_user_id, wallet_id):
    """Deduct wallet balance (internal use)"""
    wallet = wallets_db.get(wallet_id)
    
    if not wallet:
        return jsonify({'error': 'Wallet not found'}), 404
    
    if wallet['user_id'] != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    amount = data.get('amount', 0)
    
    if amount <= 0:
        return jsonify({'error': 'Invalid amount'}), 400
    
    if wallet['balance'] < amount:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    wallet['balance'] -= amount
    
    return jsonify({
        'message': 'Deduction successful',
        'wallet': wallet
    })

@app.route('/wallets/user/<int:user_id>', methods=['GET'])
@token_required
def get_wallet_by_user(current_user_id, user_id):
    """Get wallet by user ID (internal use)"""
    for wallet in wallets_db.values():
        if wallet['user_id'] == user_id:
            return jsonify({'wallet': wallet})
    
    return jsonify({'error': 'Wallet not found'}), 404

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=True)
