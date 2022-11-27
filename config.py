from flask import Flask
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret"
jwt = JWTManager(app)

from blueprint import api_blueprint, errors

app.register_blueprint(api_blueprint)
app.register_blueprint(errors)
