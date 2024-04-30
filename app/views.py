import logging
from datetime import timedelta

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app import mongo

api_bp = Blueprint('api', __name__)

logging.basicConfig(filename='access.log', level=logging.INFO)

@api_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = generate_password_hash(data.get('password'))

    user = mongo.db.users.find_one({'email': email})
    if user:
        return jsonify({'message': 'User already exists!'}), 400

    mongo.db.users.insert_one({'name': name, 'email': email, 'password': password})
    return jsonify({'message': 'User registered successfully!'}), 201

@api_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = mongo.db.users.find_one({'email': email})
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid credentials!'}), 401

    access_token = create_access_token(identity=email, expires_delta=timedelta(minutes=30))
    logging.info(f"Access token generated for user: {email}.\nAccess token: {access_token}")
    return jsonify(access_token=access_token), 200

@api_bp.route('/logout', methods=['GET'])
@jwt_required()
def logout():
    # Perform logout actions if needed
    return jsonify({'message': 'Logged out successfully!'}), 200
