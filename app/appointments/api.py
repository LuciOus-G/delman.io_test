from datetime import datetime

from flask import Blueprint, jsonify, request
from app.models import Appointments, User
from app import schema, Error
from flask_pydantic import validate
from app import db
from app.helpers import err_response
from app.helpers import login_require


appointment_route = Blueprint('appointment', __name__)
# register API for appointment

@appointment_route.route('/appointment', methods=['GET', 'POST'])
@validate()
@login_require
def reg_doctors(body: schema.appointmentSchemas):
    method_type = request.method

    if method_type == 'POST':
        try:
            # validation
            date_time = datetime.strptime(body.datetime, '%d/%m/%y %H:%M')
            get_dotcor_data = User.query.filter_by(id=body.doctor_id, user_type='doctor').first()
            get_any_apointment = Appointments.query.filter_by(
                datetime=date_time
            ).all()

            if get_any_apointment:
                return err_response(
                    error_code=400,
                    message="the doctor has schedule in that time"
                )

            if (date_time.time() < get_dotcor_data.work_start_time) or \
                    (date_time.time() > get_dotcor_data.work_end_time):
                return err_response(
                    error_code=400,
                    message="the appoinment date is outside doctor work time"
                )

            user_data = Appointments(
                patien_id=body.patient_id,
                doctor_id=body.doctor_id,
                datetime=date_time,
                status =body.status,
                diagnose=body.diagnose,
                notes=body.notes
            )

            db.session.add(user_data)
            db.session.commit()

            generate_response = schema.appointmentResponse().dump(user_data)
            return jsonify(generate_response)
        except Exception as e:
            raise Error(
                message='something went wrong with error: {0}'.format(e),
                status_code=400
            )


    if method_type == 'GET':
        get_data = Appointments.query.all()
        if get_data:
            all_appointment = [
                schema.appointmentResponse().dump(appointment)\
                for appointment in get_data
            ]
            return jsonify(all_appointment)
        else:
            raise Error(
                message='Could not find the data',
                status_code=404
            )


@appointment_route.route('/appointment/<id>', methods=['GET', 'PUT', 'DELETE'])
@login_require
def get_doctors(id):
    method_type = request.method
    get_data = Appointments.query.get(id)

    if not get_data:
        raise Error(
            message='Could not find the data',
            status_code=404
        )

    if method_type == 'GET':
        generate_response = schema.appointmentResponse().dump(get_data)

        return jsonify(generate_response)

    if method_type == 'PUT':
        payload = dict(request.get_json())

        if get_data:
            for k, v in payload.items():
                setattr(get_data, k, v)

            db.session.add(get_data)
            db.session.commit()
            return schema.appointmentResponse().dump(get_data)

    if method_type == 'DELETE':
        if get_data:
            db.session.delete(get_data)
            db.session.commit()

        return ''