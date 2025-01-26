import faker
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import os

db = SQLAlchemy()
DB_NAME = "database.db"

fake = faker.Faker()
def load_admin(id):
    if id == "sysadmin":
        # Creează un obiect temporar pentru sysadmin
        class AdminUser:
            is_authenticated = True
            is_active = True
            is_anonymous = False
            id = "sysadmin"
            role = "admin"  # Rol specific pentru sysadmin

            def get_id(self):
                return self.id

        return AdminUser()

    return None

def load_honey_user(id):
    if id == 0:
        class HoneyUser:
            is_authenticated = True
            is_active = True
            is_anonymous = False
            id = 0
            role = "user"
            email = fake.email()
            first_name = fake.first_name()
            last_name = fake.last_name()

            def get_id(self):
                return self.id
        return HoneyUser()


def create_app():
    app = Flask(__name__)
    # genereaza o cheie secreta diferita la fiecare repornire
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Note
    
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        # verifica daca este utilizatorul sysadmin
        admin_user = load_admin(id)
        if admin_user:
            return admin_user
        honey_user = load_honey_user(id)
        if honey_user:
            return honey_user
        # Pentru utilizatorii din baza de date
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
