from flask import Flask, Blueprint, render_template, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from db import db
from db.models import users


app = Flask(__name__)

@app.route('/')
def main():
    username = (users.query.first()).username
    return render_template('main_list.html', username=username)
