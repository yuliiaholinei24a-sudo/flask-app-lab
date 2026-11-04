import os

from flask import Flask
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "dev-secret-key-change-me"
)

csrf = CSRFProtect(app)

from . import views

from .users import user_bp
app.register_blueprint(user_bp)

from .products import product_bp
app.register_blueprint(product_bp)
