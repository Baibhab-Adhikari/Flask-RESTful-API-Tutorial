"""
Main entry point for the Flask REST API application.
Initializes Flask, Flask-Smorest, registers Blueprints, and sets up Swagger UI.
"""

import os
import secrets

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_smorest import Api  # type: ignore

from db import db
# Importing blueprints from the resources package
from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint


def create_app(db_url=None):  # db_url parameter for database configuration flexibility
    """Flask application factory pattern."""

    app = Flask(__name__)  # Initialize Flask app

    # Configure Flask app

    # Propagate exceptions from extensions
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"  # API title for Swagger UI
    app.config["API_VERSION"] = "v1"  # API version
    app.config["OPENAPI_VERSION"] = "3.0.3"  # OpenAPI specification version
    app.config["OPENAPI_URL_PREFIX"] = "/"  # Root path for OpenAPI docs
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/docs"  # Path for Swagger UI
    # Swagger UI CDN
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    # Configure SQLAlchemy database URI, using provided db_url, environment variable, or a default SQLite DB
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv(
        "DATABASE_URL", "sqlite:///data.db")
    # Disable SQLAlchemy event system, which is not needed and adds overhead
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)  # Initialize Flask-SQLAlchemy extension
    api = Api(app)  # Initialize Flask-Smorest

    # Generate a random secret key for JWT signing.
    app.config["JWT_SECRET_KEY"] = str(secrets.SystemRandom().getrandbits(128))
    # Initialize Flask-JWT-Extended extension for handling JSON Web Tokens.
    jwt = JWTManager(app)

    with app.app_context():  # Application context is required for database operations
        db.create_all()  # Create database tables based on models, if they don't exist

    # Register blueprints for API resources
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)

    return app
