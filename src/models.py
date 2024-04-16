from unicodedata import category
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=True, default=True)

    def __repr__(self):
        return f'<User {self.first_name}>'

    def serialize(self):
        # Example serialization method
        return {
            "id": self.id,
            "first_name": self.first_name,
            "email": self.email,
            
        }

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)
    quantity = db.Column(db.Integer, unique=False, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))

    def __repr__(self):
        return f'<Product {self.title}>'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)
    quantity = db.Column(db.Integer, unique=False, nullable=False)

    products = db.relationship("Product", backref="category", lazy=True)

    def __repr__(self):
        return f'<Category {self.title}>'

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }