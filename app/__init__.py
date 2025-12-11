from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    @app.route("/ping")
    def ping():
        return {"status": "ok"}

    from . import models        # ensures models are registered
    from .routes import api_bp  # import the blueprint

    app.register_blueprint(api_bp)  # no prefix: routes are /events, /incidents

    return app
