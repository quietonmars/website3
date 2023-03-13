import os.path

from flask import Flask, request, redirect, url_for, Blueprint
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, login_required, current_user
from werkzeug.security import generate_password_hash


db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['UPLOAD_FOLDER'] = "static/uploads/"

    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import Staff, Department, Comments, Category, Notifications, Admin, Ideas, Like, Settings

    with app.app_context():
        db.create_all()
        if not Department.query.all():
            db.session.add(Department(id=1, name='Management'))
            db.session.commit()
        if not Admin.query.all():
            password = generate_password_hash('Orange1234$', method='sha256')
            admin = Admin(name='Admin', nrc='Admin NRC', type='SuperAdmin', email='superadmin@example.com',
                          phone_no='123456789', address='Admin Address', username='superadmin', password=password,
                          department_id=1, status='approved')
            db.session.add(admin)
            db.session.commit()

    login_manager = LoginManager()
    login_manager.login_view = ('auth.login')
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        staff = Staff.query.get(int(id))
        if staff:
            return staff
        admin = Admin.query.get(int(id))
        if admin and admin.status == 'approved':
            return admin
        return None

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
        with app.app_context():
            db.session.add(Department(id=1, name='Management'))
            password = generate_password_hash('Orange1234$', method='sha256')
            admin = Admin(name='Admin', nrc='Admin NRC', type='SuperAdmin', email='superadmin@example.com',
                          phone_no='123456789', address='Admin Address', username='superadmin', password=password,
                          department_id=1, status='approved')
            db.session.add(admin)
            db.session.commit()
