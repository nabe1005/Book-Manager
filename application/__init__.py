from flask import Flask
from flask_login import LoginManager

from application.database import initialize_database
from application.models import User, Book, Category
from application.auth import auth as auth_blueprint
from application.main import main as main_blueprint
from application.books import books as books_blueprint


def create_app():
    app = Flask(__name__)
    app.config.from_object('application.config.Config')
    initialize_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'このページにアクセスするにはログインしてください'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(email):
        return User.query.get(str(email))

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(books_blueprint)

    return app


app = create_app()
