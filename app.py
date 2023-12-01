from flask import Flask, Blueprint, render_template, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from db import db
from db.models import users


app = Flask(__name__)


app.secret_key = '123'
user_db = "mgskym_rgz_web"
host_ip = "localhost"
host_port = "5432"
database_name = "pharmacy_database"
password = "333"

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user_db}:{password}@{host_ip}:{host_port}/{database_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def main():
    username = (users.query.first())
    return render_template('main_list.html', username=username)
