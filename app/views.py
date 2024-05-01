import os
import logging
from datetime import timedelta

from flask import Blueprint, request, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Resource, Api
import pandas as pd

from app import mongo, jwt
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
        # Create the access token
        access_token = create_access_token(identity=email, expires_delta=timedelta(minutes=30))
        logging.info(f"Access token generated for user: {email}.\nAccess token: {access_token}")
        # Append 'Bearer ' prefix to the access token
        access_token_with_prefix = 'Bearer ' + access_token

        return {'access_token': access_token_with_prefix}, 200

class Logout(Resource):
    @jwt_required()
    def get(self):
        # Perform logout actions if needed
        current_user = get_jwt_identity()
        jti = get_jwt()['jti']
        
        # Add token to the list of revoked tokens
        mongo.db.revoked_tokens.insert_one({'jti': jti, 'user': current_user})

        return {'message': 'Logged out successfully!'}, 200

# Add token revocation loader
@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return mongo.db.revoked_tokens.find_one({'jti': jti}) is not None

class CompaniesResource(Resource):
    @jwt_required()
    def post(self):
        data = request.json
        name = data.get('name')
        website = data.get('website')
        linkedin = data.get('linkedin')
        x = data.get('x')
        country = data.get('country')
        description = data.get('description')

        existing_company_with_website = Company.find_by_website(website)
        if existing_company_with_website:
            return {'message': 'A company with the same website already exists!'}, 400

        existing_company_with_linkedin = Company.find_by_linkedin(linkedin)
        if existing_company_with_linkedin:
            return {'message': 'A company with the same LinkedIn already exists!'}, 400

        existing_company_with_x = Company.find_by_x(x)
        if existing_company_with_x:
            return {'message': 'A company with the same X already exists!'}, 400

        company = Company(name, website, linkedin, x, country, description)
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
            'x': data.get('x'),
            'country': data.get('country'),
            'description': data.get('description')
        }
        Company.update_company(company_id, new_data)
        return {'message': 'Company updated successfully!'}, 200

    def delete(self, company_id):
        Company.delete_company(company_id)
        return {'message': 'Company deleted succesfully!'}, 200

class UploadCompany(Resource):
    @jwt_required()
    def post(self):
        # Check if a file is included in the request
        if 'file' not in request.files:
            return {'message': 'No file uploaded'}, 400

        file = request.files['file']

        # Check if the file is a CSV file
        if file.filename == '':
            return {'message': 'No file selected'}, 400
        if not file.filename.endswith('.csv'):
            return {'message': 'File must be a CSV file'}, 400
        
        # Log the name of the uploaded file
        file_name = file.filename
        current_app.logger.info(f"Uploading CSV file: {file_name}")

        # Read the CSV file into a Pandas DataFrame
        try:
            df = pd.read_csv(file)

            # Iterate over each row in the DataFrame
            for index, row in df.iterrows():
                name = row['name']
                website = row['website']
                linkedin = row['linkedin']
                x = row['x']
                country = row['country']
                description = row['description']

                # Check for existing companies
                existing_company_with_website = Company.find_by_website(website)
                if existing_company_with_website:
                    continue  # Skip adding duplicate companies

                existing_company_with_linkedin = Company.find_by_linkedin(linkedin)
                if existing_company_with_linkedin:
                    continue  # Skip adding duplicate companies

                existing_company_with_x = Company.find_by_x(x)
                if existing_company_with_x:
                    continue  # Skip adding duplicate companies

                # Add the company to the database
                company = Company(name, website, linkedin, x, country, description)
                company.save_to_db()

            return {'message': 'Companies added successfully'}, 201

        except Exception as e:
            current_app.logger.error(f"Error processing file: {e}")
            return {'message': 'Error processing file'}, 500

api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CompaniesResource, '/companies')
api.add_resource(CompanyResource, '/companies/<company_id>')
api.add_resource(UploadCompany, '/upload')