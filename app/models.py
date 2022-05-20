from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import TIME, ENUM
#
# # Models and timestampmixin
class Models(object):
    id = db.Column(db.Integer, primary_key=True)

class Timestampmixin(object):
    created = db.Column(db.DateTime, default=datetime.utcnow)
    modified = db.Column(db.DateTime, onupdate=datetime.utcnow, default=datetime.utcnow)

class User(db.Model, Models, Timestampmixin):
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    gender = db.Column(db.String, nullable=False)
    birthdate = db.Column(db.DateTime, default=datetime.now)

    # for doctors
    work_start_time = db.Column(TIME())
    work_end_time = db.Column(TIME())

    # additional column for validation purpose
    salt = db.Column(db.String)
    user_type = db.Column(db.String)

class Patients(db.Model, Models, Timestampmixin):
    name = db.Column(db.String, nullable=False)
    no_ktp = db.Column(db.String, unique=True, nullable=False)
    gender = db.Column(db.String, nullable=False)
    birthdate = db.Column(db.DateTime, default=datetime.now)
    address = db.Column(db.String)

class Appointments(db.Model, Models, Timestampmixin):

    APPOINTMENT_STATUS = {
        'IN_QUEUE': 'IN_QUEUE',
        'DONE': 'DONE',
        'CANCELLED': 'CANCELLED'
    }

    patien_id = db.Column(db.Integer, db.ForeignKey('patients.id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    datetime = db.Column(db.DateTime)
    status = db.Column(ENUM(*APPOINTMENT_STATUS.values(), name='appointment_status'), nullable=False)
    diagnose = db.Column(db.String)
    notes = db.Column(db.String)