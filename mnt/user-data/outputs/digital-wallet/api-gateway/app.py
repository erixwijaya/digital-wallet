from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Service URLs
USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://localhost:5001')
WALLET_SERVICE_URL = os.getenv('WALLET_SERVICE_URL', 'http://localhost:5002')
TRANSACTION_SERVICE_URL = os.getenv('TRANSACTION_SERVICE_URL', 'http://localhost:5003')
PAYMENT_SERVICE_URL = os.getenv('PAYMENT_SERVICE_URL', 'http://localhost:5004')

# Request timeout in seconds
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 5))

def forward_request(service_url, path, method, headers=None, json_data=None):
    """Forward request to microservice with timeout"""
    url = f"{service_url}{path}"
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=json_data, timeout=REQUEST_TIMEOUT)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=json_data, timeout=REQUEST_TIMEOUT)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=REQUEST_TIMEOUT)
        else:
            return jsonify({'error': 'Method not allowed'}), 405
        
        return response.json(), response.status_code
    
    except requests.exceptions.Timeout:
        return jsonify({
            'error': 'Request timeout',
            'message': f'Service did not respond within {REQUEST_TIMEOUT} seconds'
        }), 504
    
    except requests.exceptions.ConnectionError:
        return jsonify({
            'error': 'Service unavailable',
            'message': 'Could not connect to the service'
        }), 503
    
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': 'Service error',
            'message': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """API Gateway health check"""
    services_status = {}
    
    # Check all services
    services = {
        'user-service': USER_SERVICE_URL,
        'wallet-service': WALLET_SERVICE_URL,
        'transaction-service': TRANSACTION_SERVICE_URL,
        'payment-service': PAYMENT_SERVICE_URL
    }
    
    for service_name, service_url in services.items():
        try:
            response = requests.get(f"{service_url}/health", timeout=2)
            services_status[service_name] = 'healthy' if response.status_code == 200 else 'unhealthy'
        except:
            services_status[service_name] = 'unreachable'
    
    all_healthy = all(status == 'healthy' for status in services_status.values())
    
    return jsonify({
        'service': 'api-gateway',
        'status': 'healthy' if all_healthy else 'degraded',
        'services': services_status
    }), 200 if all_healthy else 503

# ==================== USER SERVICE ROUTES ====================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login endpoint"""
    headers = {'Content-Type': 'application/json'}
    return forward_request(USER_SERVICE_URL, '/auth/login', 'POST', headers, request.get_json())

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register endpoint"""
    headers = {'Content-Type': 'application/json'}
    return forward_request(USER_SERVICE_URL, '/auth/register', 'POST', headers, request.get_json())

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    headers = {'Authorization': request.headers.get('Authorization')}
    return forward_request(USER_SERVICE_URL, '/users', 'GET', headers)

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID"""
    headers = {'Authorization': request.headers.get('Authorization')}
    return forward_request(USER_SERVICE_URL, f'/users/{user_id}', 'GET', headers)

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user"""
    headers = {
        'Authorization': request.headers.get('Authorization'),
        'Content-Type': 'application/json'
    }
    return forward_request(USER_SERVICE_URL, f'/users/{user_id}', 'PUT', headers, request.get_json())

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user"""
    headers = {'Authorization': request.headers.get('Authorization')}
    return forward_request(USER_SERVICE_URL, f'/users/{user_id}', 'DELETE', headers)

@app.route('/api/users/verify', methods=['GET'])
def verify_user():
    """Verify user token"""
    headers = {'Authorization': request.headers.get('Authorization')}
    return forward_request(USER_SERVICE_URL, '/users/verify', 'GET', headers)

# ==================== WALLET SERVICE ROUTES ====================

@app.route('/api/wallets', methods=['GET'])
def get_wallets():
    headers = {'Authorization': request.headers.get('Authorization')}
    return forward_request(WALLET_SERVICE_URL, '/wallets', 'GET', headers)

@app.route('/api/wallets/<int:wallet_id>', methods=['GET'])
def get_wallet(wallet_id):
    headers = {'Authorization': request.headers.get('Authorization')}
    return forward_request(WALLET_SERVICE_URL, f'/wallets/{wallet_id}', 'GET', headers)

@app.route('/api/wallets/<int:wallet_id>/topup', methods=['POST'])
def topup_wallet(wallet_id):
    headers = {
        'Authorization': request.headers.get('Authorization'),
        'Content-Type': 'application/json'
    }
    return forward_request(WALLET_SERVICE_URL, f'/wallets/{wallet_id}/topup', 'POST', headers, request.get_json())

# ==================== TRANSACTION SERVICE ROUTES ====================

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """Get all transactions"""
    headers = {'Authorization': request.headers.get('Authorization')}
    return forward_request(TRANSACTION_SERVICE_URL, '/transactions', 'GET', headers)

@app.route('/api/transactions/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """Get transaction by ID"""
    headers = {'Authorization': request.headers.get('Authorization')}
    return forward_request(TRANSACTION_SERVICE_URL, f'/transactions/{transaction_id}', 'GET', headers)

@app.route('/api/transactions/wallet/<int:wallet_id>', methods=['GET'])
def get_transactions_by_wallet(wallet_id):
    """Get transactions by wallet"""
    headers = {'Authorization': request.headers.get('Authorization')}
    return forward_request(TRANSACTION_SERVICE_URL, f'/transactions/wallet/{wallet_id}', 'GET', headers)

@app.route('/api/transactions/stats', methods=['GET'])
def get_transaction_stats():
    """Get transaction statistics"""
    headers = {'Authorization': request.headers.get('Authorization')}
    return forward_request(TRANSACTION_SERVICE_URL, '/transactions/stats', 'GET', headers)

# ==================== PAYMENT SERVICE ROUTES ====================

@app.route('/api/payments', methods=['GET'])
def get_payments():
    """Get all payments"""
    headers = {'Authorization': request.headers.get('Authorization')}
    return forward_request(PAYMENT_SERVICE_URL, '/payments', 'GET', headers)

@app.route('/api/payments/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    """Get payment by ID"""
    headers = {'Authorization': request.headers.get('Authorization')}
    return forward_request(PAYMENT_SERVICE_URL, f'/payments/{payment_id}', 'GET', headers)

@app.route('/api/payments/pay', methods=['POST'])
def process_payment():
    """Process payment"""
    headers = {
        'Authorization': request.headers.get('Authorization'),
        'Content-Type': 'application/json'
    }
    return forward_request(PAYMENT_SERVICE_URL, '/payments/pay', 'POST', headers, request.get_json())

@app.route('/api/payments/transfer', methods=['POST'])
def process_transfer():
    """Process transfer"""
    headers = {
        'Authorization': request.headers.get('Authorization'),
        'Content-Type': 'application/json'
    }
    return forward_request(PAYMENT_SERVICE_URL, '/payments/transfer', 'POST', headers, request.get_json())

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5050))
    app.run(host='0.0.0.0', port=port, debug=True)
