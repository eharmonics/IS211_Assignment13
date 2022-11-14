from datetime import datetime
from . import db

class Students(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    
    def __str__(self):
        return (self.id,self.first_name)

class Quizzes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(30))
    questions = db.Column(db.Text)
    time = db.Column(db.DateTime)
    
    def __str__(self):
        return f"{self.subject,self.time}"

class QuizResults(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, nullable=False)
    student_id = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer)
    
    def __str__(self):
        return f"{self.quiz_id,self.student_id,self.score}"

class Teachers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30))
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    password = db.Column(db.String(30))
    
    def __str__(self):
        return f"{self.id,self.username,self.first_name}"
