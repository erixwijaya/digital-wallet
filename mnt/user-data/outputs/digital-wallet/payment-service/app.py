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
TRANSACTION_SERVICE_URL = os.getenv('TRANSACTION_SERVICE_URL', 'http://localhost:5003')
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 5))

# Database pembayaran (in-memory)
payments_db = {
    1: {
        'id': 1,
        'user_id': 1,
        'wallet_id': 1,
        'merchant': 'Tokopedia',
        'amount': 50000,
        'status': 'completed',
        'payment_method': 'wallet',
        'created_at': '2024-01-03T14:30:00'
    }
}

next_payment_id = 2

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

def deduct_wallet(wallet_id, amount, token):
    """Deduct amount from wallet"""
    try:
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        response = requests.post(
            f'{WALLET_SERVICE_URL}/wallets/{wallet_id}/deduct',
            json={'amount': amount},
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        return response.status_code == 200
    except requests.exceptions.Timeout:
        return False
    except requests.exceptions.RequestException:
        return False

def topup_wallet(wallet_id, amount, token):
    """Top up wallet"""
    try:
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        response = requests.post(
            f'{WALLET_SERVICE_URL}/wallets/{wallet_id}/topup',
            json={'amount': amount},
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        return response.status_code == 200
    except requests.exceptions.Timeout:
        return False
    except requests.exceptions.RequestException:
        return False

def create_transaction_record(wallet_id, trans_type, amount, description, token):
    """Create transaction record"""
    try:
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        response = requests.post(
            f'{TRANSACTION_SERVICE_URL}/transactions',
            json={
                'wallet_id': wallet_id,
                'type': trans_type,
                'amount': amount,
                'description': description
            },
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        return response.status_code == 201
    except requests.exceptions.Timeout:
        return False
    except requests.exceptions.RequestException:
        return False

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'service': 'payment-service',
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat()
    })

@app.route('/payments', methods=['GET'])
@token_required
def get_payments(current_user_id):
    """Get all payments for current user"""
    user_payments = [
        p for p in payments_db.values() 
        if p['user_id'] == current_user_id
    ]
    
    user_payments.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify({'payments': user_payments})

@app.route('/payments/<int:payment_id>', methods=['GET'])
@token_required
def get_payment(current_user_id, payment_id):
    """Get payment by ID"""
    payment = payments_db.get(payment_id)
    
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    
    if payment['user_id'] != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({'payment': payment})

@app.route('/payments/pay', methods=['POST'])
@token_required
def process_payment(current_user_id):
    """Process payment"""
    global next_payment_id
    
    data = request.get_json()
    print("Received data:", data)
    required_fields = ['wallet_id', 'merchant', 'amount']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    # Verify wallet
    wallet = get_wallet_info(data['wallet_id'], token)
    print("Wallet info:", wallet)
    if not wallet or wallet['user_id'] != current_user_id:
        return jsonify({'error': 'Invalid wallet'}), 400
    
    # Check balance
    if wallet['balance'] < data['amount']:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    # Deduct from wallet
    if not deduct_wallet(data['wallet_id'], data['amount'], token):
        return jsonify({'error': 'Payment processing failed'}), 500
    
    # Create payment record
    new_payment = {
        'id': next_payment_id,
        'user_id': current_user_id,
        'wallet_id': data['wallet_id'],
        'merchant': data['merchant'],
        'amount': data['amount'],
        'status': 'completed',
        'payment_method': 'wallet',
        'created_at': datetime.datetime.now().isoformat()
    }
    payments_db[next_payment_id] = new_payment
    next_payment_id += 1
    
    # Create transaction record
    create_transaction_record(
        data['wallet_id'],
        'payment',
        data['amount'],
        f"Payment to {data['merchant']}",
        token
    )
    
    return jsonify({
        'message': 'Payment successful',
        'payment': new_payment
    }), 201

@app.route('/payments/transfer', methods=['POST'])
@token_required
def process_transfer(current_user_id):
    """Process transfer between wallets"""
    data = request.get_json()
    
    required_fields = ['from_wallet_id', 'to_user_id', 'amount']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    # Verify source wallet
    from_wallet = get_wallet_info(data['from_wallet_id'], token)
    if not from_wallet or from_wallet['user_id'] != current_user_id:
        return jsonify({'error': 'Invalid source wallet'}), 400
    
    # Check balance
    if from_wallet['balance'] < data['amount']:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    # Get destination wallet
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(
            f'{WALLET_SERVICE_URL}/wallets/user/{data["to_user_id"]}',
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        if response.status_code != 200:
            return jsonify({'error': 'Destination user not found'}), 404
        to_wallet = response.json().get('wallet')
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timeout'}), 504
    except requests.exceptions.RequestException:
        return jsonify({'error': 'Service unavailable'}), 503
    
    # Deduct from source
    if not deduct_wallet(data['from_wallet_id'], data['amount'], token):
        return jsonify({'error': 'Transfer failed'}), 500
    
    # Add to destination
    if not topup_wallet(to_wallet['id'], data['amount'], token):
        # Rollback source deduction
        topup_wallet(data['from_wallet_id'], data['amount'], token)
        return jsonify({'error': 'Transfer failed'}), 500
    
    # Create transaction records
    create_transaction_record(
        data['from_wallet_id'],
        'transfer',
        data['amount'],
        f"Transfer to user {data['to_user_id']}",
        token
    )
    
    return jsonify({
        'message': 'Transfer successful',
        'from_wallet_id': data['from_wallet_id'],
        'to_wallet_id': to_wallet['id'],
        'amount': data['amount']
    }), 201

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5004))
    app.run(host='0.0.0.0', port=port, debug=True)
