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
WALLET_SERVICE_URL = os.getenv('WALLET_SERVICE_URL', 'http://localhost:5002')
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 5))

# Database transaksi (in-memory)
transactions_db = {
    1: {
        'id': 1,
        'user_id': 1,
        'wallet_id': 1,
        'type': 'topup',
        'amount': 500000,
        'description': 'Initial top up',
        'status': 'completed',
        'created_at': '2024-01-01T10:00:00'
    },
    2: {
        'id': 2,
        'user_id': 2,
        'wallet_id': 2,
        'type': 'topup',
        'amount': 300000,
        'description': 'Initial top up',
        'status': 'completed',
        'created_at': '2024-01-02T11:00:00'
    },
    3: {
        'id': 3,
        'user_id': 1,
        'wallet_id': 1,
        'type': 'payment',
        'amount': 50000,
        'description': 'Payment for service',
        'status': 'completed',
        'created_at': '2024-01-03T14:30:00'
    }
}

next_transaction_id = 4

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

def get_wallet_info(wallet_id, token):
    """Get wallet information from wallet service"""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(
            f'{WALLET_SERVICE_URL}/wallets/{wallet_id}',
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        if response.status_code == 200:
            return response.json().get('wallet')
        return None
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.RequestException:
        return None

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'service': 'transaction-service',
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat()
    })

@app.route('/transactions', methods=['GET'])
@token_required
def get_transactions(current_user_id):
    """Get all transactions for current user"""
    user_transactions = [
        t for t in transactions_db.values() 
        if t['user_id'] == current_user_id
    ]
    
    # Sort by created_at descending
    user_transactions.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify({'transactions': user_transactions})

@app.route('/transactions/<int:transaction_id>', methods=['GET'])
@token_required
def get_transaction(current_user_id, transaction_id):
    """Get transaction by ID"""
    transaction = transactions_db.get(transaction_id)
    
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    
    if transaction['user_id'] != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({'transaction': transaction})

@app.route('/transactions', methods=['POST'])
@token_required
def create_transaction(current_user_id):
    """Create new transaction"""
    global next_transaction_id
    
    data = request.get_json()
    print(f"Creating transaction for user {current_user_id}: {data}")

    # Verify wallet belongs to user
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    wallet = get_wallet_info(data['wallet_id'], token)
    print(f"Wallet info: {wallet}")


    required_fields = ['wallet_id', 'type', 'amount', 'description']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Verify wallet belongs to user
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    wallet = get_wallet_info(data['wallet_id'], token)
    
    if not wallet or wallet['user_id'] != current_user_id:
        return jsonify({'error': 'Invalid wallet'}), 400
    
    # Validate transaction type
    if data['type'] not in ['topup', 'payment', 'transfer', 'withdrawal']:
        return jsonify({'error': 'Invalid transaction type'}), 400
    
    # Validate amount
    if data['amount'] <= 0:
        return jsonify({'error': 'Invalid amount'}), 400
    
    new_transaction = {
        'id': next_transaction_id,
        'user_id': current_user_id,
        'wallet_id': data['wallet_id'],
        'type': data['type'],
        'amount': data['amount'],
        'description': data['description'],
        'status': 'completed',
        'created_at': datetime.datetime.now().isoformat()
    }
    
    transactions_db[next_transaction_id] = new_transaction
    next_transaction_id += 1
    
    return jsonify({'transaction': new_transaction}), 201

@app.route('/transactions/wallet/<int:wallet_id>', methods=['GET'])
@token_required
def get_transactions_by_wallet(current_user_id, wallet_id):
    """Get all transactions for a specific wallet"""
    # Verify wallet belongs to user
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    wallet = get_wallet_info(wallet_id, token)
    
    if not wallet or wallet['user_id'] != current_user_id:
        return jsonify({'error': 'Invalid wallet'}), 403
    
    wallet_transactions = [
        t for t in transactions_db.values() 
        if t['wallet_id'] == wallet_id
    ]
    
    wallet_transactions.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify({'transactions': wallet_transactions})

@app.route('/transactions/stats', methods=['GET'])
@token_required
def get_transaction_stats(current_user_id):
    """Get transaction statistics for current user"""
    user_transactions = [
        t for t in transactions_db.values() 
        if t['user_id'] == current_user_id
    ]
    
    total_transactions = len(user_transactions)
    total_topup = sum(t['amount'] for t in user_transactions if t['type'] == 'topup')
    total_payment = sum(t['amount'] for t in user_transactions if t['type'] == 'payment')
    total_transfer = sum(t['amount'] for t in user_transactions if t['type'] == 'transfer')
    
    return jsonify({
        'total_transactions': total_transactions,
        'total_topup': total_topup,
        'total_payment': total_payment,
        'total_transfer': total_transfer,
        'net_amount': total_topup - total_payment - total_transfer
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5003))
    app.run(host='0.0.0.0', port=port, debug=True)
