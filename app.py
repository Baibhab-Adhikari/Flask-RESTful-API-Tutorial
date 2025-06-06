"""
Main entry point for the Flask REST API application.
Initializes Flask, Flask-Smorest, registers Blueprints, and sets up Swagger UI.
"""

import os

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_smorest import Api  # type: ignore

from db import db
# Importing blueprints from the resources package
from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint


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

    # secret key for JWT signing.
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    # Initialize Flask-JWT-Extended extension for handling JSON Web Tokens.
    jwt = JWTManager(app)

    # functions to handle JWT related errors

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Handles expired tokens. Called when JWT is expired."""
        return (
            jsonify({
                "message": "The token has expired",
                "error": "Token expired"
            }),
            401
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """Handles invalid/tampered tokens. Called when JWT is invalid"""
        return (
            jsonify({
                "message": "Signature verification failed.",
                "error": "Invalid token"
            }),
            401
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """Handles missing tokens. Called when no JWT is present"""
        return (
            jsonify({
                "description": "Request does not contain an access token.",
                "error": "authorization_required."
            }),
            401
        )

    # JWT claims are pieces of information (e.g., user roles, permissions)
    # encoded within the JWT payload. This function adds custom claims.
    @jwt.additional_claims_loader
    # 'identity' is the value passed to create_access_token
    def add_claims_to_jwt(identity):
        """Adds custom claims to JWT tokens when they are created.

        This function determines if a user has admin privileges based on their ID.
        It's called automatically whenever a new JWT token is generated.

        Args:
            identity: The user identifier (typically user.id) passed to create_access_token()

        Returns:
            dict: A dictionary of claims to add to the JWT payload
        """

        # This is a simplified check: user with ID 1 is considered an admin.
        # In a real application, this logic would typically involve checking a database
        # or a configuration file to determine a user's admin status.
        if identity == 1:
            return {"is_admin": True}
        return {"is_admin": False}

    with app.app_context():  # Application context is required for database operations
        db.create_all()  # Create database tables based on models, if they don't exist

    # Register blueprints for API resources
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app
