from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from datetime import date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ANY POWERFUL KEY'

db = SQLAlchemy(app=app)

from .models import *
#with app.app_context(): 
#    db.create_all()
#    t = Teachers(username="teacher1",first_name="Jack",last_name="Woy",password="12345")
#    db.session.add(t)
#    db.session.commit()

def is_teacher_in(f):
    @wraps(f) 
    def wrap(*args, **kwargs):
        if 'username' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('panel'))
    return render_template('home.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == "POST":
        username = request.form.get('name')
        pswd = request.form.get('password')
        t = Teachers.query.filter_by(username=username).first()
        if t:
            if pswd == t.password:
                print("yes")
                session['username'] = t.username
                return redirect(url_for('panel'))
            flash('Incorrect password!', 'error')
        flash('No teacher found!', 'error')
    return render_template('login.html')

@app.route('/panel')
@is_teacher_in
def panel():
    return render_template('panel.html')

@app.route('/add-student',methods=['GET','POST'])
@is_teacher_in
def add_student():
    if request.method == "POST":
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        st = Students.query.filter_by(first_name=fname,last_name=lname).first()
        if st:
            flash(f'{fname+" "+lname} is already present!','error')
        else:
            new = Students(first_name=fname,last_name=lname)
            db.session.add(new)
            db.session.commit()
            flash('Quiz Added!','success')
            return redirect(url_for('panel'))
    return render_template('add_student.html')

@app.route('/view-students')
@is_teacher_in
def view_students():
    students = Students.query.all()
    return render_template('view_students.html',students=students)

@app.route('/add-quiz',methods=['GET','POST'])
@is_teacher_in
def add_quiz():
    if request.method == "POST":
        sub = request.form.get('subject')
        questions = request.form.get('questions')
        quiz = Quizzes(subject=sub,questions=questions,time=date.today())
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz Added!','success')
        return redirect(url_for('panel'))
    return render_template('add_quiz.html')

@app.route('/view-quizzes')
@is_teacher_in
def view_quizzes():
    quizzes = Quizzes.query.all()
    results = QuizResults.query.all()
    done = []
    for i in results:
        done.append(str(i.quiz_id))
    done=set(done)
    done = list(done)
    return render_template('view_quizzes.html',done=done, quizzes=quizzes)

@app.route('/evaluate/<q>',methods=['GET','POST'])
@is_teacher_in
def evaluate(q):
    q = int(q)
    if request.method == "POST":
        quiz = request.form.get('quiz-id')
        marks = request.form.getlist('marks')
        ids = request.form.getlist('ids') 
        for i in range(len(ids)):
            res = QuizResults(student_id=int(ids[i]),quiz_id=int(quiz),score=int(marks[i]))
            print("done")
            db.session.add(res)
            db.session.commit()
        return redirect(url_for('view_quizzes'))
    resulted = QuizResults.query.all()
    for i in resulted:
        if i.quiz_id == q:
            flash('Results already given!','error')
            return redirect(url_for('view_quizzes'))
    quiz = Quizzes.query.filter_by(id=q).first()
    students = Students.query.all()
    return render_template('evaluate.html', quiz=quiz,students=students)

@app.route('/view-results')
@is_teacher_in
def view_results():
    students = Students.query.all()
    quizzes = Quizzes.query.all()
    results = QuizResults.query.all()
    return render_template('view_quizzes.html', quizzes=quizzes)

@app.route('/logout')
@is_teacher_in
def logout():
    session.pop('username',None)
    return redirect(url_for('home'))

@app.route('/submit-marks',methods=["POST"])
@is_teacher_in
def submit_marks():
    try:
        id = request.form.get('id')
        marks = request.form.get('marks')
        quiz_id = request.form.get('quizid')
        print(id,marks,quiz_id,"**")
        res = QuizResults(quiz_id=int(quiz_id), student_id=int(id),score=int(marks))
        db.session.add(res)
        db.session.commit()
        return jsonify({'success':'yes'})
    except Exception as e:
        print(e)
        return jsonify({'error':'yes'})
    
@app.route('/results/<id>')
def results(id):
    id_ = int(id)
    res = QuizResults.query.filter_by(quiz_id=id_).all()
    final_res = {}
    for i in res:
        t = Students.query.filter_by(id=i.student_id).first()
        final_res.update({t:i.score})
    return render_template('results.html', results=final_res)