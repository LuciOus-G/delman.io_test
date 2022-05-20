from pydantic import BaseModel
from typing import Any
from app import ma
from app import models

class employeesSchemas(BaseModel):
    name: str
    username: str
    password: str
    gender: str
    birthdate: Any

class doctorsSchemas(BaseModel):
    name: str
    username: str
    password: str
    gender: str
    birthdate: Any
    work_start_time: Any
    work_end_time: Any

class usersResponse(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.User
        include_fk = True

class patientSchemas(BaseModel):
    name: str
    no_ktp: str
    gender: str
    birthdate: Any
    address: str

class patientResponse(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.Patients
        include_fk = True

class appointmentSchemas(BaseModel):
    patient_id: int
    doctor_id: int
    diagnose: str
    notes: str
    datetime: Any
    status: Any

class appointmentResponse(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.Appointments
        include_fk = True

class loginSchemas(BaseModel):
    username: str
    password: str