from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from datetime import date
import random
import MySQLdb.cursors
import re
from datetime import date

app = Flask(__name__)


app.secret_key = 'employee_system'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'emp'

mysql = MySQL(app)

@app.route('/', methods =['GET', 'POST'])
def index():
    if request.method=='POST' and 'email' in request.form and 'pass' in request.form:
        email = request.form['email']
        passw = request.form['pass']
        print(email)
        print(passw)
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM admin WHERE email = %s AND password = %s", (email, passw))
        data = cur.fetchone()
        if data:
            session['email'] = email
            session['loggedin'] = True
            return redirect(url_for('home'))
    return render_template('index.html') 


@app.route('/home', methods =['GET', 'POST'])
def home():
    if session.get('loggedin'):
        msg = request.args.get('msg')
        print(msg)
        if msg:
            return render_template('home.html',msg=msg)
        return render_template('home.html')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('email', None)
	return redirect(url_for('index'))

@app.route('/aaddemp', methods =['GET', 'POST'])
def addemp():
    msg=''
    if session.get('loggedin'):
        msg=''
        if request.method == 'POST' and 'name' in request.form and 'mobile' in request.form and 'email' in request.form and 'address' in request.form and 'jd' in request.form and 'years' in request.form and 'degree' in request.form and 'desig' in request.form :
            name = request.form['name']
            mobile = request.form['mobile']
            email = request.form['email']
            address = request.form['address']
            jd = request.form['jd']
            years = request.form['years']
            degree = request.form['degree']
            desig = request.form['desig']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO addemp VALUES (NULL,%s, %s, %s, %s, %s, %s, %s, %s)', (name, email, address, jd, mobile, years, degree, desig))
            mysql.connection.commit()
            msg = 'Employee Added Successfuly'
            return redirect(url_for('home', msg=msg))
        return render_template('addemp.html')
    return redirect(url_for('index'))

@app.route('/emplist')
def emplist():
    if session.get('loggedin'):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM addemp')
        empdata = cursor.fetchall()
        return render_template('emplist.html', empdata=empdata)
    return redirect(url_for('index'))

@app.route('/deleteemp', methods =['GET', 'POST'])
def deleteemp():
    if request.method == 'POST' and 'emp_id' in request.form:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        emp_id = request.form['emp_id']
        cur.execute("DELETE FROM addemp WHERE id = %s", (emp_id))
        cur.fetchone()
        mysql.connection.commit()
        return '1'

@app.route('/presentemp',  methods =['GET', 'POST'])
def presentemp():
    if request.method == 'POST' and 'emp_id' in request.form:
        emp_id = request.form['emp_id']
        curdate = date.today()
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('INSERT INTO attendance VALUES (NULL,%s, %s, %s)', (emp_id, curdate, 1))
        mysql.connection.commit()
        return '1'

@app.route('/absentemp',  methods =['GET', 'POST'])
def absentemp():
    if request.method == 'POST' and 'emp_id' in request.form:
        emp_id = request.form['emp_id']
        curdate = date.today()
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('INSERT INTO attendance VALUES (NULL,%s, %s, %s)', (emp_id, curdate, 0))
        mysql.connection.commit()
        return '1'

@app.route('/attendance')
def attendance():
    if session.get('loggedin'):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM addemp')
        empdata = cursor.fetchall()
        return render_template('attendance.html', empdata=empdata)
    return redirect(url_for('index'))

@app.route('/generate',  methods =['GET', 'POST'])
def generate(): 
    if request.method == 'POST' and 'emp_id' in request.form:
        emp_id = request.form['emp_id']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM attendance WHERE emp_id = %s ', (emp_id))
        data = cur.fetchone()
        if data:
            total_days = cur.rowcount
            cur.execute('SELECT * FROM attendance WHERE emp_id = %s AND attendance = 1 ', (emp_id))
            present_days = cur.rowcount
            cur.execute('SELECT * FROM attendance WHERE emp_id = %s AND attendance = 0 ', (emp_id))
            absent_days = cur.rowcount
            total_days = str(total_days)
            present_days = str(present_days)
            absent_days = str(absent_days)
            cur.execute('SELECT * FROM addemp WHERE id = %s ', (emp_id))
            data = cur.fetchone()
            name = data['name']
            mobile = data['mobile']
            desig = data['desig'] 
            data = {
                'name': name,
                'mobile': mobile,
                'desig': desig,
                'total_days': total_days,
                'present_days': present_days,
                'absent_days': absent_days
            }
            return data

@app.route('/search',  methods =['GET', 'POST'])
def search():
    if session.get('loggedin'):
        if request.method == 'POST' and 'name' in request.form:
            name = request.form['name'] 
            print(name)
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute('SELECT * FROM addemp WHERE id = %s ', (name,))
            data = cur.fetchone()
            return data
        return render_template('search.html')
    return redirect(url_for('index'))

def getusertodayatten(user_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    today = date.today()
    today = str(today)
    cur.execute('SELECT * FROM attendance WHERE emp_id = %s AND date = %s', (user_id,today))
    data = cur.fetchone()
    if data:
        return 1
    else:
        return 2
app.jinja_env.globals.update(getusertodayatten=getusertodayatten) 

@app.route('/update')
def update():
    if session.get('loggedin'):
        emp_id = request.args.get('emp_id')
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM addemp WHERE id = %s ', (emp_id,))
        data = cur.fetchone()
        return render_template('update.html', empdata=data)
    return redirect(url_for('index'))

@app.route('/updateemp', methods =['GET', 'POST'])
def updateemp():
    if request.method == 'POST' and 'emp_id' in request.form and 'empname' in request.form and 'mobile' in request.form and 'desig' in request.form and 'address' in request.form and 'email' in request.form and 'years' in request.form and 'degree' in request.form and 'jd' in request.form:
        emp_id = request.form['emp_id']
        name = request.form['empname']
        mobile = request.form['mobile']
        desig = request.form['desig']
        address = request.form['address']
        email = request.form['email']
        years = request.form['years']
        degree = request.form['degree']
        jd = request.form['jd']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('UPDATE addemp SET name = %s, mobile = %s, desig = %s, address = %s, email = %s, years = %s, degree = %s, jd = %s WHERE id = %s', (name, mobile, desig, address, email, years, degree, jd, emp_id))
        mysql.connection.commit()
        return '1'
    return redirect(url_for('index'))
            