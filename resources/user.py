from flask.views import MethodView
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt, get_jwt_identity, jwt_required)
from flask_smorest import Blueprint, abort  # type: ignore
from passlib.hash import pbkdf2_sha256  # type: ignore
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import JWTBlocklist, UserModel
from schemas import UserSchema

blp = Blueprint("Users", "users", "Operations on API users.")


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):

        # check if user exists in DB
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            # HTTP 409 Conflict: Indicates the request cannot be processed due to a conflict
            # with the current state of the resource (e.g., username already exists).
            abort(409, exc="A user with that name already exists.")

        # if not, then hash pw and insert into DB

        user = UserModel(
            username=user_data["username"],
            password=pbkdf2_sha256.hash(user_data["password"]),
        )

        db.session.add(user)
        db.session.commit()

        # 201 created HTTP code for successful registration
        return {"message": "User registered successfully."}, 201


# USER RESOURCE FOR TESTING ONLY -> NOT FOR PUBLIC

@blp.route("/user/<int:user_id>")
class User(MethodView):
    """
    This resource can be useful when testing our Flask app.
    We may not want to expose it to public users, but for the
    sake of demonstration in this course, it can be useful
    when we are manipulating data regarding the users.
    """

    @blp.response(200, UserSchema)
    def get(self, user_id):
        return UserModel.query.get_or_404(user_id)

    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()

        return {"message": "User deleted"}, 200


# user login class view
@blp.route("/login")
class UserLogin(MethodView):
    """Handles user authentication and token generation.

    Provides an endpoint for users to log in by submitting their credentials.
    Upon successful authentication, it generates and returns a fresh JWT access token
    and a refresh token.
    """
    @blp.arguments(UserSchema)  # Expects user data matching the UserSchema (typically username and password)
    def post(self, user_data):
        """Authenticates a user and returns JWT tokens.

        Args:
            user_data (dict): A dictionary containing the user's login credentials,
                              validated against the UserSchema. Expected keys are
                              'username' and 'password'.

        Returns:
            tuple: A dictionary containing the 'access_token' and 'refresh_token',
                   and an HTTP 200 OK status code upon successful login.

        Raises:
            401 Unauthorized: If the provided credentials are invalid (user not found
                              or password does not match).
        """
        # Find the user in the database by their username.
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()

        # Verify if the user exists and if the provided password matches the stored hash.
        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            # If authentication is successful, create a new JWT access token.
            # The 'identity' for the token is set to the user's ID (converted to a string).
            # 'fresh=True' indicates this token was generated from a direct login.
            access_token = create_access_token(
                identity=str(user.id), fresh=True)
            # Create a new JWT refresh token, also using the user's ID as identity.
            # Refresh tokens are typically longer-lived and used to obtain new access tokens.
            # Pass user.id directly, it will be handled.
            refresh_token = create_refresh_token(identity=str(user.id))
            # Return both the access token and the refresh token.
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        # If authentication fails (user not found or password incorrect),
        # abort the request with a 401 Unauthorized error.
        abort(401, message="Invalid credentials.")


# user logout class view
@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]  # get the JWT ID claim from the token
        blocked_jwt = JWTBlocklist(jti=jti)
        try:
            db.session.add(blocked_jwt)
            db.session.commit()
            return {"message": "Logout successful"}
        except SQLAlchemyError as e:
            abort(400, exc=str(e))

# token refresh route


@blp.route("/refresh")
class TokenRefresh(MethodView):
    """Handles refreshing of JWT access tokens.

    This endpoint allows a client to obtain a new access token by
    presenting a valid refresh token. This is useful for maintaining
    user sessions without requiring frequent re-authentication.
    The refresh token used is blocklisted after a new access token is issued.
    """
    @jwt_required(refresh=True)  # This decorator ensures that only a valid refresh token can access this endpoint.
    def post(self):
        """Generates a new non-fresh access token using a valid refresh token.

        The identity from the refresh token is used to create the new access token.
        The refresh token itself is then added to the blocklist to prevent reuse.

        Returns:
            dict: A dictionary containing the new 'access_token'.
            int: HTTP 200 OK status code.

        Raises:
            400 Bad Request: If there's a database error during blocklisting.
            401 Unauthorized: If the refresh token is invalid, expired, or not provided.
        """
        # Get the identity of the user from the refresh token.
        current_user_identity = get_jwt_identity()

        # Create a new access token. It's marked as non-fresh (fresh=False)
        # because it's generated from a refresh token, not direct credentials.
        new_access_token = create_access_token(
            identity=current_user_identity, fresh=False)

        # Get the JTI (JWT ID) of the refresh token that was just used.
        # This JTI will be added to the blocklist to invalidate the refresh token.
        used_refresh_token_jti = get_jwt()["jti"]

        # Create a JWTBlocklist entry for the used refresh token.
        blocklisted_refresh_token = JWTBlocklist(jti=used_refresh_token_jti)

        try:
            # Add the blocklist entry to the database session and commit.
            db.session.add(blocklisted_refresh_token)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(
                400, exc=f"Database error while blocklisting token: {str(e)}")

        # Return the new access token.
        return {"access_token": new_access_token}, 200
