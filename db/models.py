from . import db
from flask_login import UserMixin

class users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(102), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"id:{self.id}, username:{self.username}, is_admin:{self.is_admin}"

class medicines(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patented_name = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    recipe_only = db.Column(db.Boolean, nullable=False)
    price = db.Column(db.Numeric, nullable=False)
    count = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"id:{self.id}, patented_name:{self.patented_name}, name:{self.name}, recipe_only:{self.recipe_only}, price:{self.price}, count:{self.count}"