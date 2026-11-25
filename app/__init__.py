import os
from pathlib import Path

from flask import Flask, render_template
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase

from .config import configurations


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
migrate = Migrate()
csrf = CSRFProtect()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message = "Будь ласка, увійдіть у систему для доступу до цієї сторінки."
login_manager.login_message_category = "warning"


def create_app(config_name=None):
    app = Flask(__name__)
    config_name = config_name or os.getenv("APP_ENV", "development")

    if config_name not in configurations:
        raise ValueError(f"Невідома конфігурація: {config_name}")

    app.config.from_object(configurations[config_name])

    if not app.config["SECRET_KEY"]:
        raise RuntimeError("Укажи SECRET_KEY у файлі .env")

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from .views import register_routes
    from .users import user_bp
    from .products import product_bp
    from .posts import post_bp

    register_routes(app)
    app.register_blueprint(user_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(post_bp)

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template(
            "404.html",
            title="Сторінку не знайдено",
        ), 404

    return app