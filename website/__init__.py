import os.path


from flask import Flask, request, redirect, url_for, Blueprint
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, login_required, current_user



db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['UPLOAD_FOLDER'] = "static/uploads/"

    # UPLOAD_FOLDER = 'static/uploads/'
    # app.secret_key = "secret key"
    # app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    # app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    # ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'docx', 'csv', 'xlsx'])


    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import Staff, Department, Comments, Category, Notifications, Admin, Ideas, Like, Settings

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Staff.query.get(int(id))

    return app



def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')



