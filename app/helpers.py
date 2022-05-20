from datetime import datetime, timedelta
import hashlib
import os, json
from binascii import hexlify, unhexlify
from google.cloud import bigquery
from flask import Response, request, g
import jwt
import os
from app.models import Patients
from app import db

from app import BASE_DIR, Error


class authHelpers(object):
    def __init__(self):
        self.secret = "thisisjwtsecret"

    def verify_password(self, new_password, prev_pass, salt):
        salts = unhexlify(salt)
        new_pass, _ = self.hashed_pass(new_password, salts)

        if new_pass == prev_pass:
            return True
        else:
            return False


    def hashed_pass(self, password: str, salt=None):
        # hashing password
        if not salt:
            salt = os.urandom(32)

        hash_pass = hashlib.scrypt(
            password=password.encode('utf-8'),
            salt=salt,
            n=16,
            r=8,
            p=1
        )

        return hexlify(hash_pass).decode('utf-8'), hexlify(salt).decode('utf-8')

    def encode_jwt(self, user):
        payload = {
            "exp": datetime.utcnow() + timedelta(minutes=15),
            "iat": datetime.utcnow(),
            "user_id": user.id
        }

        return jwt.encode(
            payload,
            self.secret,
            algorithm='HS256'
        )

    def decode_jwt(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms='HS256')
            return payload
        except jwt.ExpiredSignatureError:
            raise Error(
                message='the token is expired.'
            )
        except jwt.InvalidTokenError as e:
            raise Error(
                message="Token signature invalid",
            )

class patientsHelper(object):
    def data_bigquery(self, filter: str = None, specific: bool = False):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(BASE_DIR, 'credentials.json')
        os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        all_data = []
        client = bigquery.Client()

        QUERY = 'SELECT * FROM `delman-interview.interview_mock_data.vaccine-data` '

        if filter:
            QUERY += filter

        job_config = bigquery.job.QueryJobConfig(use_query_cache=False)
        query_job = client.query(QUERY, job_config)
        rows = query_job.result()

        for row in rows:
            all_data.append(row)

        if len(all_data) == 1 and specific:
            all_data = all_data[0]
        
        return all_data

    def auto_update_bigquery(self):
        data = self.data_bigquery()
        for row in data:
            get_patients = Patients.query.filter_by(no_ktp=row.no_ktp)
            if get_patients:
                for k, v in dict(row).items():
                    try:
                        setattr(get_patients, k, v)
                        db.session.add(get_patients)
                        db.session.commit()
                    except:
                        pass
            else:
                pass

# catxh error
dtserializer = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None
def err_response(error_code=400, message=''):
    rv = json.dumps(
        {
            'status_code': error_code,
            'message': message,
        }, default=dtserializer)
    return Response(rv, status=error_code, mimetype='application/json')

# decorator auth
def login_require(func):
    def wrapper(*args, **kwargs):
        # if not g.testing:
        token = request.headers.get("Authorization", None)

        if token:
            token = token.split('Bearer ')[1]

        if not token:
            raise Error(
                message="token unavailable"
            )


        verify_token = authHelpers().decode_jwt(token)

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper