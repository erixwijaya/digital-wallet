from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import datetime
from functools import wraps
import os

app = Flask(__name__)


CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)



# Secret key untuk JWT
SECRET_KEY = os.getenv('SECRET_KEY', 'digital-wallet-secret-key-2024')

# Database sederhana (in-memory)
users_db = {
    1: {
        'id': 1,
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone': '081234567890',
        'password': 'password123'
    },
    2: {
        'id': 2,
        'name': 'Jane Smith',
        'email': 'jane@example.com',
        'phone': '081234567891',
        'password': 'password123'
    },
    3: {
        'id': 3,
        'name': 'Bob Wilson',
        'email': 'bob@example.com',
        'phone': '081234567892',
        'password': 'password123'
    }
}

next_user_id = 4

# Decorator untuk verifikasi JWT
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

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'service': 'user-service',
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat()
    })

@app.route('/auth/login', methods=['POST'])
def login():
    """Login endpoint - generate JWT token"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    # Cari user berdasarkan email
    user = None
    for u in users_db.values():
        if u['email'] == data['email']:
            user = u
            break
    
    if not user or user['password'] != data['password']:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Generate JWT token
    token = jwt.encode({
        'user_id': user['id'],
        'email': user['email'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, SECRET_KEY, algorithm='HS256')
    
    return jsonify({
        'token': token,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'phone': user['phone']
        }
    })

@app.route('/auth/register', methods=['POST'])
def register():
    """Register new user"""
    global next_user_id
    data = request.get_json()
    
    required_fields = ['name', 'email', 'phone', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'All fields required'}), 400
    
    # Check if email already exists
    for u in users_db.values():
        if u['email'] == data['email']:
            return jsonify({'error': 'Email already registered'}), 400
    
    # Create new user
    new_user = {
        'id': next_user_id,
        'name': data['name'],
        'email': data['email'],
        'phone': data['phone'],
        'password': data['password']
    }
    users_db[next_user_id] = new_user
    next_user_id += 1
    
    # Generate token
    token = jwt.encode({
        'user_id': new_user['id'],
        'email': new_user['email'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, SECRET_KEY, algorithm='HS256')
    
    return jsonify({
        'token': token,
        'user': {
            'id': new_user['id'],
            'name': new_user['name'],
            'email': new_user['email'],
            'phone': new_user['phone']
        }
    }), 201

@app.route('/users', methods=['GET'])
@token_required
def get_users(current_user_id):
    """Get all users (protected)"""
    users_list = [
        {
            'id': u['id'],
            'name': u['name'],
            'email': u['email'],
            'phone': u['phone']
        }
        for u in users_db.values()
    ]
    return jsonify({'users': users_list})

@app.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user_id, user_id):
    """Get user by ID (protected)"""
    user = users_db.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'phone': user['phone']
        }
    })

@app.route('/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(current_user_id, user_id):
    """Update user (protected)"""
    if current_user_id != user_id:
        return jsonify({'error': 'Unauthorized to update this user'}), 403
    
    user = users_db.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update fields
    if 'name' in data:
        user['name'] = data['name']
    if 'phone' in data:
        user['phone'] = data['phone']
    
    return jsonify({
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'phone': user['phone']
        }
    })

@app.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(current_user_id, user_id):
    """Delete user (protected)"""
    if current_user_id != user_id:
        return jsonify({'error': 'Unauthorized to delete this user'}), 403
    
    if user_id not in users_db:
        return jsonify({'error': 'User not found'}), 404
    
    del users_db[user_id]
    return jsonify({'message': 'User deleted successfully'})

@app.route('/users/verify', methods=['GET'])
@token_required
def verify_user(current_user_id):
    """Verify token and return user info"""
    user = users_db.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'phone': user['phone']
        }
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
