import logging
from datetime import timedelta

from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Resource, Api
from app import mongo
from app.models import Company

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

logging.basicConfig(filename='access.log', level=logging.INFO)

class Register(Resource):
    def post(self):
        data = request.json
        name = data.get('name')
        email = data.get('email')
        password = generate_password_hash(data.get('password'))

        user = mongo.db.users.find_one({'email': email})
        if user:
            return {'message': 'User already exists!'}, 400

        mongo.db.users.insert_one({'name': name, 'email': email, 'password': password})
        return {'message': 'User registered successfully!'}, 201

class Login(Resource):
    def post(self):
        data = request.json
        email = data.get('email')
        password = data.get('password')

        user = mongo.db.users.find_one({'email': email})
        if not user or not check_password_hash(user['password'], password):
            return {'message': 'Invalid credentials!'}, 401

        access_token = create_access_token(identity=email, expires_delta=timedelta(minutes=30))
        logging.info(f"Access token generated for user: {email}.\nAccess token: {access_token}")
        return {'access_token': access_token}, 200

class Logout(Resource):
    @jwt_required()
    def get(self):
        # Perform logout actions if needed
        return {'message': 'Logged out successfully!'}, 200

class CompaniesResource(Resource):
    @jwt_required()
    def post(self):
        data = request.json
        name = data.get('name')
        website = data.get('website')
        linkedin = data.get('linkedin')
        country = data.get('country')
        description = data.get('description')

        existing_company_with_website = Company.find_by_website(website)
        if existing_company_with_website:
            return {'message': 'A company with the same website already exists!'}, 400

        existing_company_with_linkedin = Company.find_by_linkedin(linkedin)
        if existing_company_with_linkedin:
            return {'message': 'A company with the same LinkedIn already exists!'}, 400

        company = Company(name, website, linkedin, country, description)
        company.save_to_db()

        return {'message': 'Company created successfully!'}, 201

    @jwt_required()
    def get(self):
        companies = Company.find_all()
        return companies, 200

class CompanyResource(Resource):
    def get(self, company_id):
        company = Company.find_by_id(company_id)
        if not company:
            return {'message': 'Company not found!'}, 404
        return company, 200

    def put(self, company_id):
        data = request.json
        new_data = {
            'name': data.get('name'),
            'website': data.get('website'),
            'linkedin': data.get('linkedin'),
            'country': data.get('country'),
            'description': data.get('description')
        }
        Company.update_company(company_id, new_data)
        return {'message': 'Company updated successfully!'}, 200

    def delete(self, company_id):
        Company.delete_company(company_id)
        return {'message': 'Company deleted succesfully!'}, 200

api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CompaniesResource, '/companies')
api.add_resource(CompanyResource, '/companies/<company_id>')
