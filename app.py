from flask import Flask,render_template,request,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
import os 
from datetime import datetime
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Student.db"
app.config["UPLOAD_FOLDER"] = "static/upload"
db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(30),nullable=False)
    email = db.Column(db.String(30),nullable=False)
    dob = db.Column(db.Date,nullable=False)
    gender = db.Column(db.String(6),nullable=False)
    roll_number = db.Column(db.String(10),nullable=False)
    admissiondate = db.Column(db.Date,nullable=False)
    course = db.Column(db.String(30),nullable=False)
    photo = db.Column(db.String(50),nullable=False)

@app.route('/')
def home():
    students = Student.query.all()

    return render_template("index.html",students=students)
    
@app.route('/add_student',methods=["GET","POST"])
def add_student():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        dob = request.form.get('dob')
        dob = datetime.strptime(dob,"%Y-%m-%d" ).date()
        gender  = request.form.get('gender')
        roll_number = request.form.get('roll_number')
        admissiondate = request.form.get('admissiondate')
        admissiondate = datetime.strptime(admissiondate,"%Y-%m-%d" ).date()

        course = request.form.get('course')
        photo = request.files['photo']
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'],photo.filename)
        photo.save(photo_path)
        student = Student(name=name,email= email,dob=dob,gender=gender,roll_number=roll_number,admissiondate=admissiondate,course=course,photo=photo.filename)
        db.session.add(student)
        db.session.commit()
        return redirect(url_for("home"))

    return render_template("add_student.html")
@app.route('/student_details/<int:student_id>', methods=["GET"])
def student_details(student_id):

    student = Student.query.get(student_id)

    
    return render_template('student_details.html',student=student)


@app.route('/update_details/<int:student_id>',methods=["GET","POST"])
def update_details(student_id):
    student= Student.query.get(student_id)
    if request.method == "POST":
       student.name = request.form.get('name')
       student.email = request.form.get('email')
       dob = request.form.get('dob')
       student.dob = datetime.strptime(dob,"%Y-%m-%d" ).date() 
       student.gender  = request.form.get('gender')
       student.roll_number = request.form.get('roll_number')
       admissiondate = request.form.get('admissiondate')
       student.admissiondate = datetime.strptime(admissiondate,"%Y-%m-%d" ).date()

       student.course = request.form.get('course')
       photo = request.files['photo']
       photo_path = os.path.join(app.config['UPLOAD_FOLDER'],photo)
       photo.save(photo_path)
       student.photo = photo.filename
       db.session.commit() 
       return redirect(url_for('home'))
    
       
    return render_template("update_details.html",student=student)

@app.route("/delete/<int:student_id>" ,methods=["GET","POST"])
def delete_student(student_id):
    student = Student.query.get(student_id)
    print(student)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'],student.photo)
    os.remove(file_path)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('home'))


with app.app_context():
    db.create_all()    
    



if __name__ == "__main__":

    app.run(debug=True)