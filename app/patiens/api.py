from flask import Blueprint, jsonify, request
from app.models import Patients
from app import schema, Error
from flask_pydantic import validate
from app import db
from app.helpers import patientsHelper, login_require
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation


patient_route = Blueprint('patient', __name__)
# register API for patients

@patient_route.route('/patients', methods=['GET', 'POST'])
@login_require
@validate()
def reg_patient(body: schema.patientSchemas):
    method_type = request.method

    if method_type == 'POST':
        try:
            patient_data = Patients(
                name = body.name,
                no_ktp=body.no_ktp,
                gender=body.gender,
                birthdate=body.birthdate,
                address=body.address
            )

            db.session.add(patient_data)
            db.session.commit()

            generate_response = schema.patientResponse().dump(patient_data)
            return jsonify(generate_response)
        except IntegrityError as e:
            assert isinstance(e.orig, UniqueViolation)
            raise Error(
                message='patients with this KTP number already registered',
                status_code=400
            )
        except Exception as e:
            raise Error(
                message='something went wrong with error: {0}'.format(e),
                status_code=400
            )


    if method_type == 'GET':
        get_data = Patients.query.all()

        if get_data:
            all_patiens = []
            for patient in get_data:
                vacine_data = patientsHelper().data_bigquery(
                    filter='where no_ktp={0}'.format(patient.no_ktp),
                    specific=True
                )
                patien_json = schema.patientResponse().dump(patient)
                patien_json['vaccine_type'] = vacine_data.vaccine_type if vacine_data else ''
                patien_json['vaccine_count'] = vacine_data.vaccine_count if vacine_data else ''

                all_patiens.append(patien_json)

            return jsonify(all_patiens)
        else:
            raise Error(
                message='Could not find the data',
                status_code=404
            )




@patient_route.route('/patients/<id>', methods=['GET', 'PUT', 'DELETE'])
@login_require
def get_patients(id):
    method_type = request.method
    get_data = Patients.query.get(id)

    if not get_data:
        raise Error(
            message='Could not find the data',
            status_code=404
        )

    vacine_data = patientsHelper().data_bigquery(filter='where no_ktp={0}'.format(get_data.no_ktp), specific=True)

    if method_type == 'GET':
        generate_response = schema.patientResponse().dump(get_data)
        generate_response['vaccine_type '] = vacine_data.vaccine_type if vacine_data else ""
        generate_response['vaccine_count'] = vacine_data.vaccine_count if vacine_data else ""

        return jsonify(generate_response)

    if method_type == 'PUT':
        payload = dict(request.get_json())
        for k, v in payload.items():
            setattr(get_data, k, v)

        db.session.add(get_data)
        db.session.commit()

        generate_response = schema.patientResponse().dump(get_data)
        generate_response['vaccine_type '] = vacine_data.vaccine_type if vacine_data else ""
        generate_response['vaccine_count'] = vacine_data.vaccine_count if vacine_data else ""

        return generate_response

    if method_type == 'DELETE':
        db.session.delete(get_data)
        db.session.commit()

        return ''