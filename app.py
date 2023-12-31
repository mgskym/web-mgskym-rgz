from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, Blueprint, render_template, request, make_response, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from db import db
from db.models import users, medicines
from flask_login import login_user, login_required, current_user, logout_user


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

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_users(user_id):
    return users.query.get(int(user_id))


@app.route("/")
@app.route("/index")
@login_required
def start():
    return redirect("/search", code=302)

@app.route("/check")
@login_required
def check_all():
    is_admin = (users.query.filter_by(id=current_user.id).first()).is_admin
    if is_admin:
        users_list = users.query.all()
        medicines_list = medicines.query.all()
        print(users_list)
        print()
        print(medicines_list)
        return "result in console!"
    else:
        return redirect("/search", code=302)

@app.route("/search", methods=['POST', 'GET'])
@login_required
def search():
    username = (users.query.filter_by(id=current_user.id).first()).username
    if request.method == 'GET':
        data = medicines.query.all()
        res_count = len(data)
        return render_template(
            'search.html',
            data = data,
            page_title = 'Поиск лекарств',
            username = username,
            res_count = res_count,
            is_logged = True,
            len_data = len(data)
        )
    else:
        name = request.form.get('name')
        price_from = 0.00
        price_to = 5000.00
        if request.form.get('price_from') != '':
            price_from = float(request.form.get('price_from'))
        if request.form.get('price_to') != '':
            price_to = float(request.form.get('price_to'))

        if request.form.get('recipe') is None:
            recipe = False
        else:
            recipe = True
        if recipe:
            data = medicines.query.filter(
                    medicines.price >= price_from,
                    medicines.price <= price_to,
                    medicines.name.ilike(f'%{name}%'),
                    medicines.recipe_only == recipe
                ).all()
        else:
            data = medicines.query.filter(
                    medicines.price >= price_from,
                    medicines.price <= price_to,
                    medicines.name.ilike(f'%{name}%')
                ).all()

        res_count = len(data)

        return render_template(
            'search.html',
            data = data,
            page_title = 'Поиск лекарств',
            username = username,
            res_count = res_count,
            is_logged = True,
            len_data = len(data)
        )

@app.route("/register", methods=['POST', 'GET'])
def register():
    errors = ''
    if request.method == 'GET':
        return render_template("register.html",
            page_title = 'Регистрация'
        )
    else:
        username_form = request.form.get("username")
        password_form = request.form.get("password")

        my_user = users.query.filter_by(username=username_form).first()
        if username_form == '' and password_form == '':
            errors = 'Заполните все поля!'
            return render_template("register.html",
                page_title = 'Регистрация',
                errors = errors
            )
        else:
            if my_user is not None:
                errors = 'Пользователь с таким логином уже существует!'
                return render_template("register.html",
                    page_title = 'Регистрация',
                    errors = errors
                )
            else:
                if len(password_form) < 5:
                    errors = 'Пароль должен быть длиннее 5 символов!'
                    return render_template("register.html",
                        page_title = 'Регистрация',
                        errors = errors
                    )
                else:
                    hashedPswd = generate_password_hash(password_form, method="pbkdf2")
                    newUser = users(username = username_form,
                        password = hashedPswd,
                        is_admin = False
                    )

                    db.session.add(newUser)
                    db.session.commit()
                    return redirect("/login")

@app.route("/login", methods=['POST', 'GET'])
def login():
    errors = ''
    if request.method == 'GET':
        return render_template("login.html",
            page_title = 'Вход'
        )
    else:
        username_form = request.form.get("username")
        password_form = request.form.get("password")

        my_user = users.query.filter_by(username=username_form).first()
        if username_form == '' and password_form == '':
            errors = 'Заполните все поля!'
            return render_template("login.html",
                page_title = 'Вход',
                errors=errors
            )
        else:
            if my_user is not None:
                if check_password_hash(my_user.password, password_form) or my_user.password == 'admin':
                    login_user(my_user, remember=False)
                    return redirect("/search")
                else:
                    errors = 'Неверный пароль!'
                    return render_template("login.html",
                        errors=errors,
                        page_title = 'Вход'
                    )
            else:
                errors = 'Пользвателя с таким именем не существует!'
                return render_template("login.html",
                    errors=errors,
                    page_title = 'Вход'
                )

        return render_template("login.html",
            page_title = 'Вход',
            errors = errors
        )

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

@app.route("/delete_account", methods = ['POST', 'GET'])
@login_required
def delete_account():
    is_admin = (users.query.filter_by(id=current_user.id).first()).is_admin
    if is_admin:
        return redirect("/search")
    else:
        username = (users.query.filter_by(id=current_user.id).first()).username
        if request.method == 'GET':
            return render_template("delete_account.html",
                page_title = 'Удаление аккаунта',
                is_logged = True,
                username = username
            )
        else:
            deletedUser = users.query.filter_by(id=current_user.id).first()
            logout_user()
            db.session.delete(deletedUser)
            db.session.commit()
            return redirect("/login", code = 302)

@app.route("/new", methods = ['POST', 'GET'])
@login_required
def new():
    is_admin = (users.query.filter_by(id=current_user.id).first()).is_admin
    if is_admin:
        username = (users.query.filter_by(id=current_user.id).first()).username
        errors = ''
        if request.method == 'GET':
            return render_template("new.html",
                page_title = 'Добавление лекарства',
                is_logged = True,
                username = username
            )
        else:
            all_ids = []
            for i in  medicines.query.all():
                all_ids.append(i.id)
            id_n = max(all_ids) + 1
            name_form = request.form.get("name")
            patent_name_form = request.form.get("patented_name")
            recipe_form = request.form.get("recipe")
            if recipe_form is None:
                recipe_form = False
            else:
                recipe_form = True
            price_form = request.form.get("price")
            if price_form != '':
                price_form = float(price_form)
            count_form = request.form.get("count")
            if name_form == '' or patent_name_form == '' or recipe_form == '' or count_form == '' or price_form == '':
                errors = 'Заполните все поля!'
                return render_template("new.html",
                    page_title = 'Добавление лекарства',
                    is_logged = True,
                    username = username,
                    errors = errors
                )
            else:
                isExist = medicines.query.filter_by(name=name_form).first()
                if isExist is not None:
                    errors = 'Лекарство с таким названием уже существует!'
                    return render_template("new.html",
                        page_title = 'Добавление лекарства',
                        is_logged = True,
                        username = username,
                        errors = errors
                    )
                else:
                    newMedicine = medicines(
                        id = id_n,
                        name = name_form,
                        patented_name = patent_name_form,
                        recipe_only = recipe_form,
                        price = price_form,
                        count = count_form
                    )

                    db.session.add(newMedicine)
                    db.session.commit()
                    return redirect("/search")
    else:
        return redirect("/search")

@app.route("/delete", methods = ['POST', 'GET'])
@login_required
def delete():
    is_admin = (users.query.filter_by(id=current_user.id).first()).is_admin
    username = (users.query.filter_by(id=current_user.id).first()).username
    if is_admin:
        data = medicines.query.all()
        id_form = request.form.get("delete")
        if request.method == 'GET':
            return render_template("delete.html",
                page_title = 'Удаление лекарств',
                is_logged = True,
                username = username,
                data = data
            )
        else:
            deletedMedicine = medicines.query.filter_by(id=id_form).first()
            db.session.delete(deletedMedicine)
            db.session.commit()

            return redirect("/delete", code=302)
    else:
        return redirect("/search")

@app.route("/edit", methods = ['POST', 'GET'])
@login_required
def edit_s():
    is_admin = (users.query.filter_by(id=current_user.id).first()).is_admin
    if is_admin:
        username = (users.query.filter_by(id=current_user.id).first()).username
        data = medicines.query.all()
        id_form = request.form.get("edit_select")
        if request.method == 'GET':
            return render_template("edit_selection.html",
                page_title = 'Редактирование лекарств',
                is_logged = True,
                username = username,
                data = data
            )
        else:
            medicine_id_edit = (medicines.query.filter_by(id=id_form).first()).id
            return redirect(f"/edit/{medicine_id_edit}", code=302)
    else:
        return redirect("/search")

@app.route("/edit/<string:medicine_id_edit>", methods = ['POST', 'GET'])
def edit(medicine_id_edit):
    is_admin = (users.query.filter_by(id=current_user.id).first()).is_admin
    if is_admin:
        username = (users.query.filter_by(id=current_user.id).first()).username
        data_edit = medicines.query.filter_by(id=medicine_id_edit).first()
        if request.method == 'GET':
            return render_template("edit.html",
                page_title = f'Редактирование лекарства "{data_edit.name}"',
                is_logged = True,
                username = username,
                data = data_edit
            )
        else:
            name_form = request.form.get("name")
            patent_name_form = request.form.get("patented_name")
            recipe_form = request.form.get("recipe")
            if recipe_form is None:
                recipe_form = False
            else:
                recipe_form = True
            price_form = request.form.get("price")
            if price_form != '':
                price_form = float(price_form)
            count_form = request.form.get("count")
            if name_form == '' or patent_name_form == '' or recipe_form == '' or count_form == '' or price_form == '':
                errors = 'Заполните все поля!'
                return render_template("edit.html",
                    page_title = f'Редактирование лекарства "{data_edit.name}"',
                    is_logged = True,
                    username = username,
                    errors = errors,
                    data = data_edit
                )
            else:
                isExist = medicines.query.filter_by(name=name_form).first()
                if isExist is not None and isExist.name != name_form:
                    errors = 'Лекарство с таким названием уже существует!'
                    return render_template("edit.html",
                        page_title = f'Редактирование лекарства "{data_edit.name}"',
                        is_logged = True,
                        username = username,
                        errors = errors,
                        data = data_edit
                    )
                else:
                    data_edit.name = name_form
                    data_edit.patented_name = patent_name_form
                    data_edit.recipe_only = recipe_form
                    data_edit.price = price_form
                    data_edit.count = count_form

                    db.session.add(data_edit)
                    db.session.commit()
                    return redirect("/search")
    else:
        return redirect("/search")

        

        