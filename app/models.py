
from flask_login import UserMixin
from app import db, manager
from datetime import datetime
from sqlalchemy import UniqueConstraint



class Journal(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    teacher_id = db.Column(db.String(300), db.ForeignKey('teachers.id'), nullable=False)
    teacher = db.relationship('Teachers', backref=db.backref('rows', lazy=True))

    discipline_id = db.Column(db.String(300), db.ForeignKey('discipline.id'), nullable=False)
    discipline = db.relationship('Discipline', backref=db.backref('rows', lazy=True))

    group_id = db.Column(db.String(300), db.ForeignKey('group.id'), nullable=False)
    group = db.relationship('Group', backref=db.backref('rows', lazy=True))

    __table_args__ = (UniqueConstraint('teacher_id', 'discipline_id', 'group_id'),)

    def __init__(self, teacher_id, discipline_id, group_id):
        self.teacher_id = teacher_id
        self.discipline_id = discipline_id
        self.group_id = group_id
    def __repr__(self):
        return '<Journal %r>' % self.id


class Student(db.Model):  # База данных студента
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    curs = db.Column(db.String(1), nullable=False)
    faculty = db.Column(db.String(30), nullable=False)
    department = db.Column(db.String(30), nullable=False)
    group = db.Column(db.String(30), nullable=False)
    card_number = db.Column(db.String(6), nullable=False)
    number_phone = db.Column(db.String(11))
    mail = db.Column(db.String(20))
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Student %r>' % self.id


class Teachers(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    post = db.Column(db.String(500), nullable=False)
    department = db.Column(db.String(200), nullable=False)
    login = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(256))

    def __repr__(self):
        return 'Teachers %r' % self.id


class Table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, default=datetime.utcnow)
    text = db.Column(db.String(200), nullable=False)
    discipline = db.Column(db.String(200), nullable=False)
    teacher = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return 'Table %r' % self.id


class Discipline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

    teacher_id = db.Column(db.String(300), db.ForeignKey('teachers.id'), nullable=False)
    teacher = db.relationship('Teachers', backref=db.backref('disciplines', lazy=True))

    def __repr__(self):
        return 'Discipline %r' % self.id


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

    def __repr__(self):
            return 'Group %r' % self.id


@manager.user_loader
def load_user(user_id):
    return Teachers.query.get(user_id)