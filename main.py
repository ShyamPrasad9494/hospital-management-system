from flask import Flask, render_template,request,session,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine,text
from sqlalchemy.orm import load_only
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user
from flask_mail import Mail,Message
import json

# with open('config.json','r') as c:
#     params = json.load(c)["params"]



local_server=True
app = Flask(__name__)
app.secret_key = 'any name'



# this is for getting unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'


#SMTP mail server settings
# app.config.update(
#     MAIL_SERVER='smtp.gmail.com',
#     MAIL_PORT='587',
#     MAIL_USER_TLs=True,
#     MAIL_USERNAME=params['gmail-user'],
#     MAIL_PASSWORD=params['gmail-password']
# )
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'your email'
app.config['MAIL_PASSWORD'] = 'your password' 
mail=Mail(app)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/hms'  # Replace with actual credentials
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 3600, 'pool_size': 10, 'max_overflow': 5}
db = SQLAlchemy(app)


# Database model
class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50))
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(1000))

class Patients(db.Model):
    pid=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50))
    name=db.Column(db.String(50))
    gender=db.Column(db.String(50))
    slot=db.Column(db.String(50))
    disease=db.Column(db.String(50))
    time=db.Column(db.String(50),nullable=False)
    date=db.Column(db.String(50),nullable=False)
    dept=db.Column(db.String(50))
    number=db.Column(db.String(50))

class Doctors(db.Model):
    did=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50))
    doctorname=db.Column(db.String(50))
    dept=db.Column(db.String(100))


#here we will pass endpoints and run functions
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/doctors',methods=['POST','GET'])
def doctors():
    if request.method == "POST":
        email=request.form.get('email')
        doctorname=request.form.get('doctorname')
        dept=request.form.get('dept')
        query2=Doctors(email=email,doctorname=doctorname,dept=dept)
        db.session.add(query2)
        db.session.commit()
        flash("INFORMATION IS STORED","warning")

    return render_template('doctor.html')


@app.route('/patients',methods=['POST','GET'])
@login_required
def patients():
    connection=db.engine.connect()
    query=text("SELECT * FROM doctors")
    doct=connection.execute(query)
    doctors_list=[]

    for d in doct:
        doctors_list.append(d)

    # doct=db.engine.execute("select * from 'doctors' ")
    # doctors_list=[]
    # for d in doct:
    #     doctors_list.append(d)
    if request.method == "POST":
        email=request.form.get('email')
        name=request.form.get('name')
        gender=request.form.get('gender')
        slot=request.form.get('slot')
        disease=request.form.get('disease')
        time=request.form.get('time')
        date=request.form.get('date')
        dept=request.form.get('dept')
        number=request.form.get('number')
        subject="HOSPITAL MANAGEMENT SYSTEM"
        query=Patients(email=email,name=name,gender=gender,slot=slot,disease=disease,time=time,date=date,dept=dept,number=number)
        db.session.add(query)
        db.session.commit()
        
        


        subject = "Booking Confirmation"
        sender_email = "spyadavmodala9494@gmail.com"
        recipient_email = email
        body = "YOUR BOOKING IS CONFIRMED WITH DETAILS "+"NAME: "+name+" GENDER: "+gender+" SLOT: "+slot+" DISEASE: "+disease+" TIME: "+time+" DATE: "+date+" DEPARTMENT: "+dept+" CONTACT DETAILS: "+number+" THANKS FOR CHOOSING US! HAVE A GOOD DAY.."

        message = Message(subject=subject, sender=sender_email, recipients=[recipient_email])
        message.body = body

        mail.send(message)

        flash("Booking Confirmed","info")

    return render_template('patient.html',doct=doctors_list)

@app.route('/bookings')
@login_required
def bookings():
    em=current_user.email
    query1 = db.session.query(Patients).filter_by(email=em).options(
        load_only(
            Patients.name,
            Patients.gender,
            Patients.slot,
            Patients.time,
            Patients.date,
            Patients.disease,
            Patients.dept,
            Patients.number
        )
    ).all()
    return render_template('booking.html',query1=query1)

@app.route("/edit/<string:pid>",methods=['POST','GET'])
@login_required
def edit(pid):
    posts=Patients.query.filter_by(pid=pid).first()
    if request.method == "POST":
        email=request.form.get('email')
        name=request.form.get('name')
        gender=request.form.get('gender')
        slot=request.form.get('slot')
        disease=request.form.get('disease')
        time=request.form.get('time')
        date=request.form.get('date')
        dept=request.form.get('dept')
        number=request.form.get('number')

        posts.email = email
        posts.name = name
        posts.gender = gender
        posts.slot = slot
        posts.disease = disease
        posts.time = time
        posts.date = date
        posts.dept = dept
        posts.number = number
        db.session.commit()
        # db.engine.execute(f"update 'patients' set 'email'='{email}','name'='{name}','gender'='{gender}','slot'='{slot}','disease'='{disease}','time'='{time}','date'='{date}','dept'='{dept}','number'='{number}' where 'patients'.'pid'={pid};")
        flash("Slot Is Updated","success")
        return redirect('/bookings')

    return render_template('edit.html',posts=posts)


@app.route("/delete/<string:pid>",methods=['POST','GET'])
@login_required
def delete(pid):
    record = Patients.query.get(pid)
    if record:
        db.session.delete(record)
        db.session.commit()
        flash("Slot Deleted Successfully", "danger")
    else:
        flash("Record not found", "danger")
    
    return redirect('/bookings')



@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == "POST":
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')
        print(username,email,password)
        user=User.query.filter_by(email=email).first()
        if user:
            flash("Email Already Exists","warning")
            return render_template('signup.html')
        encpassword=generate_password_hash(password)
        # new_user=db.engine.execute(f"INSERT INTO 'user' ('username','email','password') VALUES ('{username}','{email}','{encpassword}')")
        new_user=User(username=username,email=email,password=encpassword)
        db.session.add(new_user)
        db.session.commit()
        flash("Signup Successful Please Login","success")
        return render_template('login.html')
    

    return render_template('signup.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == "POST":  
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login successful","primary")
            return redirect(url_for('index'))
        else:
            flash("invalid credentials","danger")
            return render_template('login.html')


    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Successfully Logged Out","warning")
    return redirect(url_for('login'))

@app.route('/test')
def test():
    try:
        Test.query.all()
        return 'my database is connected'
    except:
        return 'my database is not connected'

@app.route('/home')
def home():
    return 'This is my home page'

app.run(debug=True)


# username=current_user.username