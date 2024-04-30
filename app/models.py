from app import db

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
