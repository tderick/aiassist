from decouple import config
from flask import Flask
from flask_caching import Cache
from flask_login import LoginManager
from flask_session import Session
from flask_wtf.csrf import CSRFProtect

from .models import User


csrf = CSRFProtect()


def create_app():
    # create and configure the app
    app = Flask(
        __name__,
        static_folder="../static",
        template_folder="../templates",
        instance_relative_config=True,
    )
    app.config.from_mapping(
        SECRET_KEY=config("APP_SECRET_KEY"),
    )

   
    # Create and initialize the Flask-Session object AFTER `app` has been configured
    csrf.init_app(app)

    # Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login_page"

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_email(user_id)

    # Register Blieprints
    from . import  auth, errors, panel

    app.register_blueprint(auth.bp)
    app.register_blueprint(panel.bp)
    app.register_blueprint(errors.bp)

    return app
