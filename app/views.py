import logging
from datetime import timedelta

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app import mongo
from app.models import Company
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

@api_bp.route('/companies', methods=['POST'])
@jwt_required()
def create_company():
    data = request.json
    name = data.get('name')
    website = data.get('website')
    linkedin = data.get('linkedin')
    country = data.get('country')
    description = data.get('description')

    existing_company_with_website = Company.find_by_website(website)
    if existing_company_with_website:
        return jsonify({'message': 'A company with the same website already exists!'}), 400

    existing_company_with_linkedin = Company.find_by_linkedin(linkedin)
    if existing_company_with_linkedin:
        return jsonify({'message': 'A company with the same LinkedIn already exists!'}), 400

    company = Company(name, website, linkedin, country, description)
    company.save_to_db()

    return jsonify({'message': 'Company created successfully!'}), 201

@api_bp.route('/companies', methods=['GET'])
@jwt_required()
def get_companies():
    companies = Company.find_all()
    return jsonify(companies), 200

@api_bp.route('/companies/<company_id>', methods=['GET'])
@jwt_required()
def get_company(company_id):
    company = Company.find_by_id(company_id)
    if not company:
        return jsonify({'message': 'Company not found!'}), 404
    return jsonify(company), 200

@api_bp.route('/companies/<company_id>', methods=['PUT'])
@jwt_required()
def update_company(company_id):
    data = request.json
    new_data = {
        'name': data.get('name'),
        'website': data.get('website'),
        'linkedin': data.get('linkedin'),
        'country': data.get('country'),
        'description': data.get('description')
    }

    Company.update_company(company_id, new_data)

    return jsonify({'message': 'Company updated successfully!'}), 200

@api_bp.route('/companies/<company_id>', methods=['DELETE'])
@jwt_required()
def delete_company(company_id):
    Company.delete_company(company_id)

    return jsonify({'message': 'Company deleted successfully!'}), 200
