from flask import Flask, Blueprint, render_template, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from db import db
from db.models import users, medicines


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
    page_title = 'Лекарства'
    username = 'Михаил'
    data = (users.query.first())
    return render_template(
        'main_list.html',
        data=data,
        username=username,
        page_title=page_title,
    )

@app.route("/check")
def check_all():
    users_list = users.query.all()
    medicines_list = medicines.query.all()
    print(users_list)
    print()
    print(medicines_list)
    return "result in console!"

@app.route("/search", methods=['POST', 'GET'])
def search():
    if request.method == 'GET':
        data = medicines.query.all()
        res_count = len(data)
        return render_template(
            'search.html',
            data = data,
            page_title = 'Поиск лекарств',
            username = 'Михаил',
            res_count = res_count
        )
    else:
        name = request.form.get('name')
        price_from = 0
        price_to = 5000
        if request.form.get('price_from') != '':
            price_from = float(request.form.get('price_from'))
        if request.form.get('price_to') != '':
            price_to = float(request.form.get('price_to'))

        recipe = request.form.get('recipe')
        
        data = medicines.query.filter(
                medicines.price >= price_from,
                medicines.price <= price_to,
                medicines.name.ilike(f'%{name}%'),
                medicines.recipe_only == recipe
            ).all()[:10]
        res_count = len(data)

        return render_template(
            'search.html',
            data = data,
            page_title = 'Поиск лекарств',
            username = 'Михаил',
            res_count = res_count
        )