from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

from app.models import User
from app import schema, Error
from flask_pydantic import validate
from app import db
from app.helpers import authHelpers
from app.helpers import login_require


user_route = Blueprint('employees', __name__)
# register API for employees and doctors

@user_route.post('/employees')
@validate()
def reg_employees(body: schema.employeesSchemas):
    hashes, salt = authHelpers().hashed_pass(body.password)
    try:
        user_data = User(
            name = body.name,
            username=body.username,
            password=hashes,
            gender=body.gender,
            birthdate=body.birthdate,
            user_type='employees',
            salt=salt
        )

        db.session.add(user_data)
        db.session.commit()

        generate_response = schema.usersResponse(exclude=['password', 'salt', 'work_start_time', 'work_end_time']).\
                            dump(user_data)
        return jsonify(generate_response)
    except IntegrityError as e:
        assert isinstance(e.orig, UniqueViolation)
        raise Error(
            message='Username already taken',
            status_code=400
        )
    except Exception as e:
        raise Error(
            message='something went wrong with error: {0}'.format(e),
            status_code=400
        )

@user_route.get('/employees')
@login_require
def get_all_data():
    get_data = User.query.filter_by(user_type='employees').all()
    if get_data:
        all_employee = [
            schema.usersResponse(exclude=['password', 'salt', 'work_start_time', 'work_end_time']).dump(employee)\
            for employee in get_data
        ]
        return jsonify(all_employee)
    else:
        raise Error(
            message='Could not find the data',
            status_code=404
        )


@user_route.route('/employees/<id>', methods=['GET', 'PUT', 'DELETE'])
@login_require
def get_employees(id):
    method_type = request.method
    get_data = User.query.get(id)

    if not get_data:
        raise Error(
            message='Could not find the data',
            status_code=404
        )

    if method_type == 'GET':
        generate_response = schema.usersResponse(exclude=['password', 'salt', 'work_start_time', 'work_end_time']).\
                            dump(get_data)

        return jsonify(generate_response)

    if method_type == 'PUT':
        payload = dict(request.get_json())
        helpers = authHelpers()

        # verify update password
        password = helpers.verify_password(
            new_password=payload.get('password'),
            prev_pass=get_data.password,
            salt=get_data.salt
        )

        if not password:
            new_password, new_salt = helpers.hashed_pass(payload.get('password'))
            payload['password'] = new_password
            payload['salt'] = new_salt
        elif password:
            payload.pop('password', None)

        if get_data:
            for k, v in payload.items():
                setattr(get_data, k, v)

            db.session.add(get_data)
            db.session.commit()
            return schema.usersResponse(exclude=['password', 'salt', 'work_start_time', 'work_end_time']).dump(get_data)
        elif not get_data:
            raise Error(
                message='Could not find the data',
                status_code=404
            )

    if method_type == 'DELETE':
        if get_data:
            db.session.delete(get_data)
            db.session.commit()
        elif not get_data:
            raise Error(
                message='Could not find the data',
                status_code=404
            )

        return ''