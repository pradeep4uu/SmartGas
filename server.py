# all the imports
import os,binascii
from flask import Flask, request, session, g, redirect, url_for, abort, \
		render_template, flash
from flaskext.mysql import MySQL
from flask_mail import Mail,Message
from config import config, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD
from werkzeug.utils import secure_filename
from flask import send_from_directory
import datetime
 
import logging
from logging.handlers import SMTPHandler
credentials = None

mysql = MySQL()
# create our little application :)

app = Flask(__name__)

for key in config:
	app.config[key] = config[key]

mail = Mail(app)
# Mail
mail.init_app(app)

if MAIL_USERNAME or MAIL_PASSWORD:
	credentials = (MAIL_USERNAME, MAIL_PASSWORD)
	mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, 'resetpass', credentials)
	mail_handler.setLevel(logging.ERROR)
	app.logger.addHandler(mail_handler)

mysql.init_app(app)
app.config.from_object(__name__)

def tup2float(tup):
	return float('.'.join(str(x) for x in tup))

def get_cursor():
	return mysql.connect().cursor()

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.route('/')
def screen():
	return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
	if request.method == "POST":
		db = get_cursor()
		username = request.form['username']
		indexQuery = 'select count(*) from Authentication'
		db.execute(indexQuery)
		value = db.fetchone()[0]
		index = value + 1
		checkQuery = 'select username from Authentication where username = "%s"'%username
		db.execute(checkQuery)
		data = db.fetchall()
		if not data:
			password = request.form['password']
			confpassword = request.form['confirmpassword']
			usertype = request.form['userType']
			verified = 0
			lastRecovery = datetime.datetime.now()
			if password == confpassword:
				insertQuery = 'insert into Authentication VALUES ("%s","%s","%s","%s","%s","%s")'
				db.execute(insertQuery%(index, username, password, usertype, verified, lastRecovery))
				db.execute("COMMIT")
				userInsertQuery = 'insert into Users (`index`) VALUES ("%s")'%index
				db.execute(userInsertQuery)
				db.execute("COMMIT")
				print "success"
				return redirect(url_for('login'))
			else:
				print "Password didnot match"
				return redirect(url_for('register'))
		else:
			print "Username already exists"
			return redirect(url_for('register'))
	return render_template('register.html')

@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/dashboard')
def dashboard():
	return render_template('dashboard.html')

@app.route('/enterprise')
def enterprise():
	return render_template('enterprise.html')

@app.route('/enterpriseprofile')
def enterpriseprofile():
	return render_template('enterpriseprofile.html')

@app.route('/successfullydelivered')
def successfullydelivered():
	return render_template('successDelivery.html')

@app.route('/undelivered')
def undelivered():
	return render_template('undelivered.html')

@app.route('/grid')
def grid():
	# Cylinders in warehouse should take us to Grid
	return render_template('grid.html')

@app.route('/invoice')
def invoice():
	return render_template('invoice.html')

@app.route('/invoices')
def invoices():
	# Shows the list of invoices of previous purchases as a table
	return render_template('invoices.html')

@app.route('/profile')
def profile():
	return render_template('profile.html')

@app.route('/editprofile')
def editprofile():
	return render_template('editprofile.html')

@app.teardown_appcontext
def close_db():
	"""Closes the database again at the end of the request."""
	get_cursor().close()

if __name__ == '__main__':
	app.debug = True
	app.secret_key=os.urandom(24)
	# app.permanent_session_lifetime = datetime.timedelta(seconds=200)
	app.run()