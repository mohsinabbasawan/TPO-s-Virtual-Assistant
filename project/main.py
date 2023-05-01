import json
#from argon2 import PasswordHasher
from flask import request
from flask import Flask, render_template, redirect,flash,session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_login import UserMixin
from flask.helpers import url_for
import pymysql
from flask_login import login_required,logout_user,login_user,login_manager,LoginManager,current_user
from werkzeug.security import generate_password_hash,check_password_hash
from urllib.request import urlopen
import pymysql
from flask_mail import Mail
import json

#database connection
local_server = True
app = Flask(__name__)
app.secret_key = "sayali"
userpass = 'mysql+pymysql://root:@'
basedir  = 'localhost'
dbname   = '/placement'
socket   = ''


with open('config.json','r') as c:
    params=json.load(c)["params"]

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],   
    MAIL_PASSWORD=params['gmail-password']
)

mail=Mail(app)

#unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'

app.config['SQLALCHEMY_DATABASE_URI'] = userpass + basedir + dbname

@login_manager.user_loader
def load_user(user_uid):
    return User.query.get(int(user_uid))
db = SQLAlchemy(app)

class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50))

class User(db.Model,UserMixin):
    def get_id(self):
           return (self.uid)
    uid=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(100),unique=True)
    password=db.Column(db.String(1000))

class ap(db.Model,UserMixin):
    def get_id(self):
           return (self.uid)
    uid=db.Column(db.Integer,primary_key=True)
    cname=db.Column(db.String(50))
    name=db.Column(db.String(50))
    email=db.Column(db.String(100),unique=True)
    mob=db.Column(db.Unicode(11))
    des=db.Column(db.String(50))
    slot=db.Column(db.DateTime)
    purpose=db.Column(db.String(50))
    def_purpose=db.Column(db.String(200))

class tr(db.Model,UserMixin):
    def get_id(self):
           return (self.uid)
    uid=db.Column(db.Integer,primary_key=True)
    cname=db.Column(db.String(50))
    name=db.Column(db.String(50))
    email=db.Column(db.String(100),unique=True)
    mob=db.Column(db.Unicode(11))
    des=db.Column(db.String(50))
    purpose=db.Column(db.String(50))
    def_purpose=db.Column(db.String(200))    

'''class Contact(db.Model):
    uid=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20))
    email=db.Column(db.String(20))
    mobile=db.Column(db.Integer)
    select1=db.Column(db.String)
    purpose=db.Column(db.String) '''

class feedback(db.Model):
    uid=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20))
    message=db.Column(db.String(100))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method=="POST":
        email=request.form.get('email')
        password=request.form.get('password')
        # print(email,password)
        encpassword=generate_password_hash(password)
        emailuser=User.query.filter_by(email=email).first()
        if emailuser:
            flash("User already exists. Please login","danger")
            return render_template("user-login.html")
        new_user=db.engine.execute(f"INSERT INTO `user` (`email`,`password`) VALUES ('{email}','{encpassword}') ")
        flash("New user added successfully, please login","primary")
        return render_template("user-login.html")
        


@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=="POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password,password):
            login_user(user)
            #flash("You have logged in successfully","primary")
            return render_template("user.html")
        else:
            flash("Invalid credentials","danger")
            return render_template("user-login.html")

#admin login
@app.route('/admin',methods=['POST','GET'])
def admin():
    if request.method=="POST":
        username=request.form.get('username')
        password=request.form.get('password')
        if (username==params['username'] and password==params['password']):
            session['username']=username
            #flash ("admin login successful","primary")
            return render_template("admindata.html")
        else:
            flash("Invalid credentials","danger")
            return render_template("admin-login.html")

@app.route('/adminfunctions',methods=['POST','GET'])
def adminfunctions():
    if('username' in session and session['username']==params['username']):
        if request.method=="POST":
            pass
            return render_template("adminfunctions.html")
        else:
            flash("Invalid credentials, login and try again","danger")
            return render_template("admin-login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout Successful","warning")
    return render_template("user-login.html")
    
@app.route('/adminlogout')
def adminlogout():
    session.pop('user')
    flash("Admin Logout Successful","warning")
    return render_template("admin-login.html")  

@app.route('/others', methods = ['GET','POST'])  
def others():
    if(request.method=='POST'):
        name=request.form.get("name")
        email=request.form.get("email")
        mobile=request.form.get("mobile")
        purpose=request.form.get("purpose")
        def_purpose=request.form.get("def_purpose")
        entry= tr(name=name,email=email,mobile=mobile,purpose=purpose, def_purpose= def_purpose)
        db.session.add(entry)
        db.session.commit()

    return render_template("others.html")

@app.route('/feedback', methods = ['GET','POST'])  
def feedback():
    if(request.method=='POST'):
        username=request.form.get("username")
        message=request.form.get("message")
        db.engine.execute(f"INSERT INTO `feedback` (`username`,`message`) VALUES ('{username}','{message}') ")

    return render_template("thanks.html")


@app.route('/appointment',methods=['POST','GET'])
def appointment():
    '''email=current_user.email
    posts=ap.query.filter_by(email=email).first()

    postsdata=ap.query.filter_by(email=code).first()'''
    if('username' in session and session['username']==params['username']):
        if request.method=="POST":
            cname=request.form.get('cname')
        name=request.form.get('name')
        email=request.form.get('email')
        mob=request.form.get('mob')
        des=request.form.get('des')
        slot=request.form.get('slot')
        purpose=request.form.get('purpose')
        def_purpose=request.form.get('def_purpose')
        emailuser=ap.query.filter_by(email=email).first()
        if emailuser:
            flash("already taken","warning")
        db.engine.execute(f"INSERT INTO `ap` (`cname`,`name`,`email`,`mob`,`des`,`slot`,`purpose`,`def_purpose`) VALUES ('{cname}','{name}','{email}','{mob}','{des}','{slot}','{purpose}','{def_purpose}') ")
        #flash("Thank you, please check your email for further details","primary")
        mail.send_message('VISITOR ADMINISTRATION CELL',sender=params['gmail-user'],recipients=[email],body=f"Thankyou, your appointment is confirmed!")
        flash("Done")
        return render_template("thanks.html")

    else:
            flash("error")

    return render_template("appointment.html")


@app.route('/trainer',methods=['POST','GET'])
def trainer():
    email=current_user.email
    posts=tr.query.filter_by(email=email).first()
    code=posts.email
    postsdata=tr.query.filter_by(email=code).first()
    if('username' in session and session['username']==params['username']):
        if request.method=="POST":
            cname=request.form.get('cname')
        name=request.form.get('name')
        email=request.form.get('email')
        mob=request.form.get('mob')
        des=request.form.get('des')
        purpose=request.form.get('purpose')
        def_purpose=request.form.get('def_purpose')
        emailuser=tr.query.filter_by(email=email).first()
        if emailuser:
            flash("already taken","warning")
        db.engine.execute(f"INSERT INTO `tr` (`cname`,`name`,`email`,`mob`,`des`,`purpose`,`def_purpose`) VALUES ('{cname}','{name}','{email}','{mob}','{des}','{purpose}','{def_purpose}') ")
        #flash("Thank you, please check your email for further details","primary")
        mail.send_message('VISITOR ADMINISTRATION CELL',sender=params['gmail-user'],recipients=[email],body=f"Thankyou,your appointment is confirmed!")
        flash("Done")
        return render_template("thanks.html")
       
    

@app.route('/adminappointment')
def adminappointment():
    #cursor = app.cursor()  
    #cursor.execute("select * from `ap`") 
    #data = cursor.fetchall() #data from database 
    #return render_template("adminappointments.html", value=data) 
    queryData = {"query" : []}
    query=db.engine.execute(f"SELECT  `cname`,`name`,`email`,`mob`,`des`,`slot`,`purpose`,`def_purpose` FROM `ap` ")
    #heading = ['uid','company name','name','email','mobile','designation', 'slot', 'purpose', 'elloboration']
    #queryData['query'].append(heading)
    for data in query:
        queryData["query"].append(data)
    print(queryData)
    return render_template("adminappointments.html",appointData=queryData)


# testint
@app.route('/test')
def test():
    global a
    try:
        a=Test.query.all()
        print(a)
        return 'MY DATABASE IS CONNECTED'
    except Exception as e:
        print(a)
        return 'MY DATABASE IS NOT CONNECTED'
        
app.run(debug=True)