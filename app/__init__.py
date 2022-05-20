import os
from datetime import datetime
from string import Template
from urllib.parse import quote_plus

from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

print("starting app")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace('\\', '/')

# base
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = Template(
        "postgresql://$user:$password@$host:$port/$db_name").substitute(
        user=os.environ.get("DB_USER", "delmanio"),
        password=quote_plus(os.environ.get("DB_PASS", "delmanio123")),
        host=os.environ.get("DB_HOST", "localhost"),
        port=os.environ.get("DB_PORT", "5433"),
        db_name=os.environ.get("DB_NAME", "delmanio_db")
    )

# Installed apps
db = SQLAlchemy(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)

# error handling
class Error(Exception):
    status_code = 400

    def __init__(self, message, status_code=status_code, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status_code'] = self.status_code
        return rv

@app.errorhandler(Error)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

# creating crontab

from apscheduler.schedulers.background import BackgroundScheduler
from app.helpers import patientsHelper

scheduler = BackgroundScheduler()
scheduler.add_job(func=patientsHelper().auto_update_bigquery, trigger="cron", second=2)
scheduler.start()

# register the blueprint
from app.employees.api import user_route
from app.doctors.api import doctor_route
from app.patiens.api import patient_route
from app.appointments.api import appointment_route
from app.auth.api import login_route

app.register_blueprint(user_route)
app.register_blueprint(doctor_route)
app.register_blueprint(patient_route)
app.register_blueprint(appointment_route)
app.register_blueprint(login_route)