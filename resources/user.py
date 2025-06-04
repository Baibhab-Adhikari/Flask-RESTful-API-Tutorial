from flask.views import MethodView
from flask_smorest import Blueprint, abort  # type: ignore
from passlib.hash import pbkdf2_sha256  # type: ignore

from db import db
from models import UserModel
from schemas import UserSchema


blp = Blueprint("Users", "users", "Operations on API users.")


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):

        # check if user exists in DB
        if UserModel.query.all(username=user_data["username"]).first():
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

@blp.route("/user/<int: user_id>")
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
