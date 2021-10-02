import datetime
import enum
import sqlalchemy.dialects.postgresql as pg

from gino_starlette import Gino
from sqlalchemy.sql import expression
from sqlalchemy_utils import ChoiceType

from assessment_src import config

db = Gino(dsn=config.DB_DSN, use_connection_for_request=False)


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer(), primary_key=True)
    fio = db.Column(db.String(50))

    is_admin = db.Column(db.Boolean())

    time_start = db.Column(
        db.DateTime(), nullable=False, default=datetime.datetime.utcnow
    )

    group_id = db.Column(db.Integer(), nullable=False)


class Teachers(db.Model):
    __tablename__ = "teachers"

    id = db.Column(db.Integer(), primary_key=True)
    fio = db.Column(db.String(50))

    time_start = db.Column(
        db.DateTime(), nullable=False, default=datetime.datetime.utcnow
    )

    group_id = db.Column(db.Integer(), nullable=False)


class University(db.Model):
    __tablename__ = "universities"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(20))

    time_start = db.Column(
        db.DateTime(), nullable=False, default=datetime.datetime.utcnow
    )


class Group(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(10))

    time_start = db.Column(
        db.DateTime(), nullable=False, default=datetime.datetime.utcnow
    )

    university_id = db.Column(db.Integer(), nullable=False)


class Exam(db.Model):
    __tablename__ = "exams"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(10))

    time_start = db.Column(
        db.DateTime(), nullable=False, default=datetime.datetime.utcnow
    )

    grade = db.Column(db.String(10))

    student_id = db.Column(db.Integer(), nullable=False)
    teacher_id = db.Column(db.Integer(), nullable=False)
