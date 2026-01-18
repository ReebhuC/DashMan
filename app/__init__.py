from flask import Flask
from flask_pymongo import PyMongo
from config import Config

mongo = PyMongo()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    mongo.init_app(app)

    @app.route("/ping")
    def ping():
        return {"status": "ok"}

    from .routes import api_bp

    app.register_blueprint(api_bp)

    return app
