import datetime

from gino_starlette import Gino

from assessment_src import config

db = Gino(dsn=config.DB_DSN, use_connection_for_request=False)


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer(), primary_key=True)
    fio = db.Column(db.String(50))
    email = db.Column(db.String(50))

    is_admin = db.Column(db.Boolean(), default=False)

    time_start = db.Column(
        db.DateTime(), nullable=False, default=datetime.datetime.utcnow
    )

    group_id = db.Column(db.Integer(), nullable=False)


class Teacher(db.Model):
    __tablename__ = "teachers"

    id = db.Column(db.Integer(), primary_key=True)
    fio = db.Column(db.String(50))
    email = db.Column(db.String(50))

    time_start = db.Column(
        db.DateTime(), nullable=False, default=datetime.datetime.utcnow
    )

    group_id = db.Column(db.Integer(), nullable=False)


class City(db.Model):
    __tablename__ = "cities"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(20))

    time_start = db.Column(
        db.DateTime(), nullable=False, default=datetime.datetime.utcnow
    )


class University(db.Model):
    __tablename__ = "universities"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(20))

    time_start = db.Column(
        db.DateTime(), nullable=False, default=datetime.datetime.utcnow
    )

    city_id = db.Column(db.Integer(), nullable=False)


class Faculty(db.Model):
    __tablename__ = "faculties"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(20))

    time_start = db.Column(
        db.DateTime(), nullable=False, default=datetime.datetime.utcnow
    )

    university_id = db.Column(db.Integer(), nullable=False)


class Group(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(10))

    time_start = db.Column(
        db.DateTime(), nullable=False, default=datetime.datetime.utcnow
    )

    faculty_id = db.Column(db.Integer(), nullable=False)


class Work(db.Model):
    __tablename__ = "works"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(10), nullable=False)

    time_start = db.Column(
        db.DateTime(), nullable=False, default=datetime.datetime.utcnow
    )
    token = db.Column(db.String(20), nullable=False, index=True)

    teacher_id = db.Column(db.Integer(), nullable=False, index=True)
    admin_id = db.Column(db.Integer(), nullable=False, index=True)
    subject_id = db.Column(db.Integer(), nullable=False, index=True)
    group_id = db.Column(db.Integer(), nullable=False, index=True)


class Grade(db.Model):
    __tablename__ = "grades"

    id = db.Column(db.Integer(), primary_key=True)
    grade = db.Column(db.String(10))

    time_start = db.Column(
        db.DateTime(), nullable=False, default=datetime.datetime.utcnow
    )

    # teacher_id = db.Column(db.Integer(), nullable=False)
    student_id = db.Column(db.Integer(), nullable=False, index=True)
    work_id = db.Column(db.Integer(), nullable=False, index=True)


class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(10))

    time_start = db.Column(
        db.DateTime(), nullable=False, default=datetime.datetime.utcnow
    )

    teacher_id = db.Column(db.Integer(), nullable=False)
    group_id = db.Column(db.Integer(), nullable=False, index=True)
