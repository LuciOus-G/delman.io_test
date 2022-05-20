from flask import Blueprint, jsonify, request
from app.models import User
from app import schema, Error
from flask_pydantic import validate
from app import db
from app.helpers import authHelpers
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation


login_route = Blueprint('login', __name__)

@login_route.post('/login')
@validate()
def login(body: schema.loginSchemas):
    # check if user is exist
    user = User.query.filter_by(username=body.username).first()
    helper = authHelpers()

    if not user:
        raise Error(
            message="user with this username does not exist",
            status_code=404
        )

    # check the password
    valid = helper.verify_password(
        new_password=body.password,
        prev_pass=user.password,
        salt=user.salt
    )

    if not valid:
        raise Error(
            message="password is wrong",
            status_code=400
        )

    token = helper.encode_jwt(user)

    return jsonify({
        "messege": "success login",
        "token": token
    })