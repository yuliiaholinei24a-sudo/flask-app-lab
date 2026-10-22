from flask import Flask

app = Flask(__name__)

from . import views

from .users import user_bp
app.register_blueprint(user_bp)