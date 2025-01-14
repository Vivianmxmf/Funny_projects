from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from functools import wraps
from cryptography.fernet import Fernet
import os

app = Flask(__name__)
CORS(app)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/password_manager'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    encryption_key = db.Column(db.String(200), nullable=False)
    passwords = db.relationship('Password', backref='user', lazy=True)

class Password(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    encrypted_password = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            data = jwt.decode(token.split()[1], app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    encryption_key = Fernet.generate_key().decode()
    hashed_password = generate_password_hash(data['password'])
    
    new_user = User(
        username=data['username'],
        password_hash=hashed_password,
        encryption_key=encryption_key
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    
    if user and check_password_hash(user.password_hash, data['password']):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'])
        
        return jsonify({
            'token': token,
            'username': user.username
        })
    
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/passwords', methods=['GET', 'POST'])
@token_required
def manage_passwords(current_user):
    if request.method == 'GET':
        passwords = Password.query.filter_by(user_id=current_user.id).all()
        return jsonify([{
            'id': p.id,
            'account': p.account,
            'username': p.username,
            'encrypted_password': p.encrypted_password
        } for p in passwords])
    
    data = request.get_json()
    f = Fernet(current_user.encryption_key.encode())
    encrypted_password = f.encrypt(data['password'].encode()).decode()
    
    new_password = Password(
        account=data['account'],
        username=data['username'],
        encrypted_password=encrypted_password,
        user_id=current_user.id
    )
    
    db.session.add(new_password)
    db.session.commit()
    
    return jsonify({'message': 'Password added successfully'}), 201

@app.route('/api/passwords/<int:id>', methods=['PUT', 'DELETE'])
@token_required
def manage_password(current_user, id):
    password = Password.query.filter_by(id=id, user_id=current_user.id).first()
    
    if not password:
        return jsonify({'message': 'Password not found'}), 404
    
    if request.method == 'DELETE':
        db.session.delete(password)
        db.session.commit()
        return jsonify({'message': 'Password deleted'})
    
    data = request.get_json()
    f = Fernet(current_user.encryption_key.encode())
    encrypted_password = f.encrypt(data['password'].encode()).decode()
    
    password.account = data['account']
    password.username = data['username']
    password.encrypted_password = encrypted_password
    password.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify({'message': 'Password updated'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 