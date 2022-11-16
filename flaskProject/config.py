from flask import Flask
from flask_jwt_extended import JWTManager
import timedelta

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret"
jwt = JWTManager(app)