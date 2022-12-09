
#Python Todo list Web Application
import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from werkzeug.utils import secure_filename


app = Flask(__name__)

#Custom secret key
app.secret_key = 'asdfghjkl'

#Database Connections
app.config['MYSQL_HOST'] = 'SamA29.mysql.pythonanywhere-services.com'
app.config['MYSQL_USER'] = 'SamA29'
app.config['MYSQL_PASSWORD'] = 'Guinness1000!'
app.config['MYSQL_DB'] = 'kanban'

#upload folder
app.config['UPLOAD_FOLDER'] = '/static/uploads/'

mysql = MySQL(app)


#Login system code taken from codeshack.io along with base .css (although .css has had some modification)
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        #create variables
        username = request.form['username']
        password = request.form['password']
        #check account exists
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        #Fetch the record
        account = cursor.fetchone()
        
        if account:
        #create session here and fetch todo
            session['loggedin'] = True
            session['pID'] = account['pID']
            session['username'] = account['username']
            session['imgloc'] = account['imgloc']
            
        #redirect to homepage
        return redirect(url_for('home'))
    else:
        msg = 'Incorrect username or password. They are case sensitive!'
        
        #LOGIN FORM HERE
    return render_template('login.html', msg=msg)

@app.route('/login/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('pID', None)
    session.pop('username', None)
    session.pop('imgloc', None)

    return redirect(url_for('login'))

@app.route('/login/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        #create account here
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        #check account exists yet
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', [username])
        account = cursor.fetchone()
        #Validation checks for the registration
        if account:
        	msg = 'Account Already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        	msg= 'Invalid email'
        elif not username or not password or not email:
        	msg = 'Please fill out the form!'
        else:
        	cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s, NULL)', (username, password, email,))
        	mysql.connection.commit()
        	msg= 'Registered!'

    return render_template('register.html', msg=msg)

@app.route('/', methods = ['GET', 'POST'])
def home():
    #check user is logged in
    if 'loggedin' in session:
    		cursor = mysql.connection.cursor()
    		cursor.execute("SELECT content, Num FROM Todo WHERE pID = %s", (session['pID'],))
    		output = cursor.fetchall()
    		cursor.close()
    #Add todo 
    if request.method == 'POST' and 'todo' in request.form:
    		print (request.form)
    		Todo2 = request.form['todo']
    		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    		cursor.execute('INSERT INTO Todo VALUES (NULL, %s, NULL, %s)', (Todo2, session['pID']))
    		mysql.connection.commit()
    #clear todo list
    if request.method == 'POST' and 'Clear' in request.form:
                dele = request.form['Clear']
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('DELETE FROM Todo WHERE pID = %s', (dele, session['pID']))
                mysql.connection.commit()
    return render_template('home.html', username=session['username'], Todo=output)
    #if user is not logged in, redirect to llogin page
    return redirect(url_for('login'))
  

@app.route('/profile', methods =['GET', 'POST'])
def profile():
	#check logged in status
	if 'loggedin' in session:
		cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE pID = %s', (session['pID'],))
		account=cursor.fetchone()
	#show profile page with account info
		if request.method == 'POST':
		#connect to database
			cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			pID=account['pID']
			imgloc=account['imgloc']
			f = request.files['imgloc']
			f.save(os.path.join('static/uploads/', secure_filename(f.filename)))
			#insert image location into database
			cursor.execute("Update `accounts` SET `accounts`.`imgloc`=%s WHERE pID = %s", (session['imgloc'], (session['pID'],)))
			mysql.connection.commit()
			return redirect(url_for('profile'))
		
		return render_template('profile.html', account=account)
	#user not logged in, redirect to login page
	return redirect(url_for('login'))
	

		
	
	

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
