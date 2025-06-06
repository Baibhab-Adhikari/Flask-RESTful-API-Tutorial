# the course uses a set data structure in python script, but I did this in DB as a challenge...

from db import db


class JWTBlocklist(db.Model):  # type: ignore
    __tablename__ = "jwt_blocklist"
    # 'jti' (JWT ID) claim of the token to be blocklisted.
    # This is typically a unique string.
    jti = db.Column(db.String(100), primary_key=True)
