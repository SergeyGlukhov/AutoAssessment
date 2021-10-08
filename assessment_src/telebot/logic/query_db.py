import string
import random

from sqlalchemy import and_

from assessment_src.models import (
    University,
    Student,
    City,
    Faculty,
    Group, Teacher, Subject, Work, Grade
)


async def create_student(data: dict, is_admin: bool = False):
    student = await Student.create(
        id=data.get("id"),
        fio=data.get("fio"),
        is_admin=is_admin,
        group_id=data.get("group_id")
    )
    return student


async def set_registration_admin_to_db(data: dict):
    city = await City.query.where(City.name == data.get("city")).gino.first()
    if not city:
        city = await City.create(name=data.get("city", None))

    university = await University.query.where(
        University.name == data.get("university")
    ).where(
        University.city_id == city.id
    ).gino.first()
    if not university:
        university = await University.create(name=data.get("university", None), city_id=city.id)

    faculty = await Faculty.query.where(
        Faculty.name == data.get("faculty")
    ).where(
        Faculty.university_id == university.id
    ).gino.first()
    if not faculty:
        faculty = await Faculty.create(name=data.get("faculty", None), university_id=university.id)

    group = await Group.query.where(
        Group.name == data.get("group")
    ).where(
        Group.faculty_id == faculty.id
    ).gino.first()
    if not group:
        group = await Group.create(name=data.get("group", None), faculty_id=faculty.id)

    student = await get_student_from_db(user_id=data.get("id"))
    if not student:
        student = await Student.create(
            id=data.get("id", None),
            fio=data.get("fio", None),
            is_admin=True,
            group_id=group.id
        )


async def get_student_from_db(user_id: int):
    student = await Student.query.where(Student.id == user_id).gino.first()
    return student


async def update_student_admin(student: Student):
    await student.update(is_admin=True).apply()


def generate_token():
    return "".join(
        random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
        for x in range(20)
    )


async def set_work_to_db(data: dict):
    student = await get_student_from_db(user_id=data.get("id"))

    teacher = await Teacher.query.where(
        and_(
            Teacher.fio == data.get("fio"),
            Teacher.group_id == student.group_id
        )
    ).gino.first()
    if not teacher:
        teacher = await Teacher.create(
            fio=data.get("fio"),
            group_id=student.group_id
        )

    subject = await Subject.query.where(
        and_(
            Subject.name == data.get("subject"),
            Subject.teacher_id == teacher.id,
            Subject.group_id == student.group_id
        )
    ).gino.first()
    if not subject:
        subject = await Subject.create(
            name=data.get("subject"),
            teacher_id=teacher.id,
            group_id=student.group_id
        )

    work = await Work.query.where(
        and_(
            Work.name == data.get("name"),
            Work.teacher_id == teacher.id,
            Work.admin_id == student.id,
            Work.subject_id == subject.id,
            Work.group_id == data.get("group_id")
        )
    ).gino.first()
    if not work:
        token = generate_token()
        work = await Work.create(
            name=data.get("work"),
            token=token,
            teacher_id=teacher.id,
            admin_id=student.id,
            subject_id=subject.id,
            group_id=data.get("group_id")
        )
    return work.token


async def get_work_from_db(token: str):
    work = await Work.query.where(Work.token == token).gino.first()
    return work


async def set_grade_to_db(data: dict):

    grade = await Grade.create(
        grade=data.get("grade"),
        student_id=data.get("id"),
        work_id=data.get("work_id")
    )


async def get_grade_from_db(user_id: int, work_id: int):
    grade = await Grade.query.where(
        and_(
            Grade.student_id == user_id,
            Grade.work_id == work_id
        )
    ).gino.first()
    return grade


async def get_works_from_db(user_id: int = None, subject_id: int = None):
    works = await Work.query.where(
        and_(
            Work.admin_id == user_id,
            Work.subject_id == subject_id
        )
    ).gino.all()
    return works


async def get_subjects_from_db(subject_id: int = None, group_id: int = None):
    subjects = None
    if group_id:
        subjects = await Subject.query.where(Subject.group_id == group_id).gino.all()
    if subject_id:
        subjects = await Subject.query.where(Subject.id == subject_id).gino.first()
    return subjects


async def get_students_grades_from_db(work_id: int):
    grades = await Grade.outerjoin(
        Student,
        Student.id == Grade.student_id
    ).select().where(Grade.work_id == work_id).gino.load(
        Student.load(grade=Grade)
    ).all()
    return grades


async def get_my_grades_from_db(student_id: int, subject_id: int):
    grades = await Grade.outerjoin(
        Work, Grade.work_id == Work.id
    ).select().where(
        Grade.student_id == student_id
    ).where(
        Work.subject_id == subject_id
    ).gino.load(Grade.load(work_name=Work.name)).query.order_by(Grade.id.desc()).gino.all()

    return grades


async def update_student_db_fio(id: int, fio: str):
    student = await Student.query.where(Student.id == id).gino.first()
    await student.update(fio=fio).apply()


async def get_admin_settings_from_db(id: int):
    settings_admin_query = Student.outerjoin(
        Group, Student.group_id == Group.id
    ).outerjoin(
        Faculty, Faculty.id == Group.faculty_id
    ).outerjoin(
        University, University.id == Faculty.university_id
    ).outerjoin(
        City, City.id == University.city_id
    ).select().where(Student.id == id).where(Student.is_admin == True)

    settings_admin = await settings_admin_query.gino.load(
        Student.load(
            group=Group.name,
            faculty=Faculty.name,
            faculty_id=Faculty.id,
            university=University.name,
            university_id=University.id,
            city=City.name,
            city_id=City.id
        )
    ).first()
    return settings_admin


async def update_city_db(id, name):
    city = await City.query.where(City.id == id).gino.first()
    await city.update(name=name).apply()


async def update_university_db(id, name):
    university = await University.query.where(University.id == id).gino.first()
    await university.update(name=name).apply()


async def update_faculty_db(id, name):
    faculty = await Faculty.query.where(Faculty.id == id).gino.first()
    await faculty.update(name=name).apply()


async def update_group_db(id, name):
    group = await Group.query.where(Group.id == id).gino.first()
    await group.update(name=name).apply()