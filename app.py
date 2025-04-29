from flask import Flask,render_template,request,url_for,redirect,jsonify,Response,make_response
from flask_sqlalchemy import SQLAlchemy
import os 
from functools import wraps
from datetime import datetime,timedelta
import jwt
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Student.db"
app.config["UPLOAD_FOLDER"] = "static/upload"
app.config['SECRET_KEY'] = "ArbaZShaikH"

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
class User(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    username= db.Column(db.String(80),unique=True,nullable=False)
    password = db.Column(db.String(256),nullable=False)


def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token = request.cookies.get('token')
        if not token:
            return render_template('login.html')
        try:
            data = jwt.decode(token,app.config['SECRET_KEY'],algorithms=["HS256"])
            g.user_id =data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({"message":"Token has expired !"})
        except jwt.InvalidTokenError:
            return jsonify({"message":"Invalid Token!"})
        
        
        return f(*args,**kwargs)
    return decorated








@app.route('/')
def home():
    
    students = Student.query.all()

    return render_template("index.html",students=students)
@app.route('/register',methods = ["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get('register_username')
        password = request.form.get('register_password')
        print(username,password)     
        exist_user = User.query.filter_by(username=username).first()
        if exist_user:
            return "User already exists" 
        new_user = User(username=username,password=password)
        print(new_user)
        db.session.add(new_user)
        db.session.commit()
        return render_template('login.html')
    return render_template('register.html')

@app.route('/login',methods = ["GET","POST"])   
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username= username).first()
        if not user:
            return jsonify({"message":"Invalid Username"})
        if user.password != password:
            return jsonify({"message":"Invalid Password"})
        expire_at  = datetime.utcnow() + timedelta(minutes=5)
        token = jwt.encode(
            {
                'user_id':user.id,
                'username':user.username,
                'exp': expire_at
            },
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )

        response = make_response(jsonify({"message":"Login Succesfull"}),200)
        response.set_cookie('token',token,expires=expire_at,httponly=True)
        return render_template('index.html')
    return render_template('login.html')

 
@app.route('/logout',methods=["GET"])
@token_required
def logout():
    response = make_response(jsonify({"message":"user_profile","username":user.username}))  
    response.delete_cookie('token')  
    return render_template('login.html')


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
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'],photo.filename)
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