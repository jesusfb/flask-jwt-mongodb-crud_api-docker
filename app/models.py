from app import mongo
from bson import ObjectId

class Item:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def save_to_db(self):
        db.items.insert_one({'name': self.name, 'description': self.description})

    @classmethod
    def find_by_name(cls, name):
        return db.items.find_one({'name': name})

    @classmethod
    def update_item(cls, name, new_description):
        db.items.update_one({'name': name}, {'$set': {'description': new_description}})

    @classmethod
    def delete_item(cls, name):
        db.items.delete_one({'name': name})

class Company:
    def __init__(self, name, website, linkedin, x, country, description):
        self.name = name
        self.website = website
        self.linkedin = linkedin
        self.x = x
        self.country = country
        self.description = description

    def save_to_db(self):
        mongo.db.companies.insert_one({
            'name': self.name,
            'website': self.website,
            'linkedin': self.linkedin,
            'x': self.x,
            'country': self.country,
            'description': self.description
        })

    @classmethod
    def find_all(cls):
        companies = list(mongo.db.companies.find())
        for company in companies:
            company['_id'] = str(company['_id'])  # Convert ObjectId to string
        return companies

    @classmethod
    def find_by_id(cls, company_id):
        try:
            company_id = ObjectId(company_id)
        except:
            return None
        company = mongo.db.companies.find_one({'_id': company_id})
        if company:
            company['_id'] = str(company['_id'])  # Convert ObjectId to string
        return company

    @classmethod
    def update_company(cls, company_id, new_data):
        mongo.db.companies.update_one({'_id': ObjectId(company_id)}, {'$set': {
            'name': new_data.get('name'),
            'website': new_data.get('website'),
            'linkedin': new_data.get('linkedin'),
            'x': new_data.get('x'),
            'country': new_data.get('country'),
            'description': new_data.get('description')
        }})

    @classmethod
    def delete_company(cls, company_id):
        mongo.db.companies.delete_one({'_id': ObjectId(company_id)})

    @classmethod
    def find_by_website(cls, website):
        return mongo.db.companies.find_one({'website': website})

    @classmethod
    def find_by_linkedin(cls, linkedin):
        return mongo.db.companies.find_one({'linkedin': linkedin})

    @classmethod
    def find_by_x(cls, x):
        return mongo.db.companies.find_one({'x': x})
