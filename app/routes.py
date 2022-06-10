from sqlalchemy.exc import IntegrityError
from flask import render_template, request, redirect, flash, url_for, session
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import db, app, manager
from app.models import Student, Discipline, Teachers, Journal

@app.route("/test")
def test():
    return render_template("/test.html")


@app.route("/relations", methods=['GET', 'POST'])
def relations():
    if request.method == 'POST':
        teacher_id = int(request.form.get('teacher'))
        student_id = int(request.form.get('student'))
        discipline_id = int(request.form.get('discipline'))
        journal = Journal(teacher_id, discipline_id, student_id)
        db.session.add(journal)
        try:
            db.session.commit()
        except IntegrityError:
            flash('Запись уже существует')
            db.session.rollback()
        else:
            flash('Запись добавлена')
    teachers = Teachers.query.all()
    disciplines = Discipline.query.all()
    students = Student.query.all()
    return render_template("/relations.html", teachers=teachers, disciplines=disciplines, students=students)


@app.route("/", methods=['GET', 'POST'])
@app.route('/home/', methods=['GET', 'POST'])   # Главная страница
def home_insert():
    if request.method == 'POST':
        data_exists = True
        selected_discipline_id = int(request.form.get('selected_discipline_id'))
    else:
        data_exists = False
        selected_discipline_id = 1

    teacher_id = current_user.get_id()
    current_teacher = Teachers.query.get(teacher_id)
    teacher_name = Teachers.query.get(teacher_id).name
    disciplines = Journal.query.join(Discipline).join(Teachers, Teachers.id == Journal.teacher_id).all()
    students = Journal.query.join(Teachers).join(Student).filter(Teachers.id == teacher_id).all()

    dn = db.session.query(Discipline).join(Journal, Teachers).all()

    for i, el in enumerate(dn):
        dn[i] = ((el.id == selected_discipline_id), dn[i])

    if data_exists:
        sn = db.session.query(Journal).join(Teachers, Student).filter(
                current_teacher.id == Teachers.id).filter(Journal.discipline_id == selected_discipline_id).all()  # Выбор студента по преподу
        return render_template("/home.html", teacher_id=teacher_id, teacher_name=teacher_name,
            disciplines=disciplines, students=students, dn=dn, sn=sn, data_exists=True)


    return render_template("/home.html", teacher_id=teacher_id, teacher_name=teacher_name,
            disciplines=disciplines, dn=dn, data_exists=False)


@app.route('/login', methods=['GET', 'POST'])   # Логин
def login_page():
    login = request.form.get('login')
    password = request.form.get('password')

    if login and password:
        user = Teachers.query.filter_by(login=login).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect('/home')
        else:
            flash('Проверьте правильность логина и пароля')
    return render_template("/login.html")


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])     # Регистрация
def register():
    name = request.form.get('name')
    login = request.form.get('login')
    post = request.form.get('post')
    department = request.form.get('department')
    password = request.form.get('password')

    if request.method == 'POST':
        if not (name or login or password):
            flash('Заполните все поля')
        else:
            hash_pwd = generate_password_hash(password)
            new_user = Teachers(name=name, login=login,post=post,department=department, password=hash_pwd)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/login')
    return render_template("/register.html")


@app.route('/display')  # Отображение студентов


def display():
    student = Student.query.order_by(Student.name.desc()).all()
    return render_template("/display.html", student=student)


@app.route('/department')  # Отображение преподователей
def teacher():
    teacher = Teachers.query.order_by(Teachers.name.desc()).all()
    return render_template("/department.html", teacher=teacher)


@app.route('/discipline')  # Отображение дисциплин
def discipline():
    discipline = Discipline.query.order_by(Discipline.name.desc()).all()
    return render_template("/discipline.html", discipline=discipline)


@app.route('/department/<int:id>')  # Детальное отображение преподователей
def teacher_detail(id):
    teacher = Teachers.query.get(id)
    return render_template("/teacher_detail.html", teacher=teacher)


@app.route('/display/<int:id>')  # Детальное отображение студентов
def display_detail(id):
    student = Student.query.get(id)
    return render_template("/display_detail.html", student=student)


@app.route('/discipline/<int:id>')  # Детальное отображение дисциплин
def discipline_detail(id):
    discipline = Discipline.query.get(id)
    return render_template("/discipline_detail.html", discipline=discipline)


@app.route('/display/<int:id>/delete')  # Удаление студентов
def student_delete(id):
    student = Student.query.get_or_404(id)
    try:
        db.session.delete(student)
        db.session.commit()
        return redirect('/display')
    except:
        return "При удалении студента произошла ошибка"


@app.route('/department/<int:id>/delete')  # Удаление преподавателя
def teacher_delete(id):
    teacher = Teachers.query.get_or_404(id)
    try:
        db.session.delete(teacher)
        db.session.commit()
        return redirect('/department')
    except:
        return "При удалении преподавателя произошла ошибка"


@app.route('/discipline/<int:id>/delete')  # Удаление дисциплины
def discipline_delete(id):
    discipline = Discipline.query.get_or_404(id)
    try:
        db.session.delete(discipline)
        db.session.commit()
        return redirect('/discipline')
    except:
        return "При удалении преподавателя произошла ошибка"


@app.route('/display/<int:id>/update', methods=['POST', 'GET'])  # Редактирование студента
def student_update(id):
    student = Student.query.get(id)
    if request.method == "POST":
        student.name = request.form['name']
        student.curs = request.form['curs']
        student.faculty = request.form['faculty']
        student.department = request.form['department']
        student.group = request.form['group']
        student.card_number = request.form['card_number']
        student.number_phone = request.form['number_phone']
        student.mail = request.form['mail']

        try:
            db.session.commit()
            return redirect("/display")
        except:
            return "При редактировании студента произошла ошибка..."
    else:
        return render_template("/student_update.html", student=student)


@app.route('/create_student', methods=['POST', 'GET'])  # Добавление студента
def create_student():
    if request.method == "POST":
        name = request.form['name']
        curs = request.form['curs']
        faculty = request.form['faculty']
        department = request.form['department']
        group = request.form['group']
        card_number = request.form['card_number']
        number_phone = request.form['number_phone']
        mail = request.form['mail']
        student = Student(name=name, curs=curs, faculty=faculty, department=department, group=group,
                          card_number=card_number, number_phone=number_phone, mail=mail)

        try:
            db.session.add(student)
            db.session.commit()
            return redirect("/display")
        except:
            return "При добавлении студента произошла ошибка..."
    else:
        return render_template("/create_student.html")


@app.route('/create_teacher', methods=['POST', 'GET'])  # Добавление преподавателя
def create_teacher():
    if request.method == "POST":
        name = request.form['name']
        post = request.form['post']
        discipline = request.form['discipline']
        department = request.form['department']
        login = request.form['login']
        password = request.form['password']

        teacher = Teachers(name=name, post=post, discipline=discipline, department=department, login=login, password= password)

        try:
            db.session.add(teacher)
            db.session.commit()
            return redirect("/department")
        except:
            return "При добавлении преподавателя произошла ошибка..."
    else:
        return render_template("/create_teacher.html")


@app.route('/create_discipline', methods=['POST', 'GET'])  # Добавление дисциплины
def create_discipline():
    if request.method == "POST":
        name = request.form['name']
        teacher = request.form['teacher']
        discipline = Discipline(name=name, teacher=Teachers.query.get(teacher))

        try:
            db.session.add(discipline)
            db.session.commit()
            return redirect("/discipline")
        except:
            return "При добавлении дисциплины произошла ошибка..."
    else:
        teachers = Teachers.query.all()
        return render_template("/create_discipline.html", teachers=teachers)

