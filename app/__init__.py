from flask import Flask
from app.config import Config
from app.extensions import db
from app.routes.api import api_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')

    with app.app_context():
        db.create_all()  # Creates tables on first run (development only)

    return app