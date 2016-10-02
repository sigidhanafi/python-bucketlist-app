from flask import Flask, render_template, json, request, redirect, session, escape
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
import datetime

app = Flask(__name__)
app.secret_key = 'my secret key'

# MySQL configuration
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'ffugm'
app.config['MYSQL_DATABASE_DB'] = 'db_learnpython_bucketlist'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

# route main, index
@app.route("/")
@app.route("/index")
def main():
	conn = mysql.connect()
	cursor = conn.cursor()
	query = "SELECT * FROM user"
	cursor.execute(query)
	data = cursor.fetchall()
	return render_template('index.html', data = data)

# route signup
@app.route('/signup')
def signup():
	return render_template('signup.html')

# route dosignup
@app.route('/doSignup', methods=['POST'])
def doSignup():
	_name = request.form['name']
	_email = request.form['email']
	_password = request.form['password']
	_hashed_password = generate_password_hash(_password)
	_bio = request.form['bio']

	if (_name and _email and _hashed_password and _bio):
		conn = mysql.connect()
		cursor = conn.cursor()
		query = "INSERT INTO user (name, username, password, bio) VALUES(%s,%s, %s, %s)"
		parameter = (_name, _email, _hashed_password, _bio)
		cursor.execute(query, parameter)
		data = cursor.fetchall()
		if len(data) is 0:
			conn.commit()
			return json.dumps({'message':'User created successfully!'})
		else:
			return json.dumps({'message':str(data[0])})
	else:
		return json.dumps({'message':'Field must be fill in!'})

# route signin
@app.route('/signin')
def signin():
	return render_template('signin.html')

# route dosignin
@app.route('/doLogin', methods = ['POST'])
def doLogin():
	try:
		_username = request.form['username']
		_password = request.form['password']

		conn = mysql.connect()
		cursor = conn.cursor()
		query = "SELECT * FROM user WHERE username = %s"
		parameter = (_username)
		cursor.execute(query, parameter)
		data = cursor.fetchall()
		if len(data) > 0:
			if check_password_hash(str(data[0][3]), _password):
				session['user'] = data[0][0]
				session['name'] = data[0][1]
				return redirect('/home')
			else :
				return render_template('error.html', error = 'Wrong email address or password.')
		else :
			return render_template('error.html', error = 'Wrong email address or password.')
	except Exception, e:
		return render_template('error.html', error = str(e))
	finally:
		cursor.close()
		conn.close()

# route home
@app.route('/home')
def home():
	if session.get('user'):
		conn = mysql.connect()
		cursor = conn.cursor()
		query = "SELECT * FROM wish WHERE user_id = %s AND status = 0"
		parameter = (session.get('user'))
		cursor.execute(query, parameter)
		uncheckedWish = cursor.fetchall()

		query = "SELECT * FROM wish WHERE user_id = %s AND status = 1"
		parameter = (session.get('user'))
		cursor.execute(query, parameter)
		checkedWish = cursor.fetchall()

		name = session.get('name')
		return render_template('home.html', uncheckedWish = uncheckedWish, checkedWish = checkedWish, name = name)
	else:
		return render_template('error.html', error = 'Unauthorized Access')

# route logout
@app.route('/logout')
def logout():
	session.pop('user', None)
	return redirect('/')


# crud route
# show add form
@app.route('/addwish')
def addwish():
	return render_template('addWish.html')

@app.route('/doAddWish', methods=['POST'])
def doAddWish():
	_title = request.form['title']
	_description = request.form['description']
	_user = session.get('user')

	conn = mysql.connect()
	cursor = conn.cursor()
	query = "INSERT INTO wish(title, description, user_id, date) VALUES(%s, %s, %s, %s)"
	today = datetime.date.today()
	parameter = (_title, _description, _user, today)
	cursor.execute(query, parameter)
	data = cursor.fetchall()
	if len(data) is 0:
		conn.commit()
		return redirect('/home')
	else:
		return render_template('error.html', error = 'Failed to add item!!!')
		

@app.route('/showWish')
def showWish():
	_id = request.args.get('id')

	conn = mysql.connect()
	cursor = conn.cursor()
	query = "SELECT * FROM wish WHERE id = %s"
	parameter = (_id)
	cursor.execute(query, parameter)
	data = cursor.fetchall()

	if len(data) > 0:
		return render_template('showWish.html', data = data)
	else:
		return render_template('error.html', error = "Wish not found!")

@app.route('/editWish')
def editWish():
	_id = request.args.get('id')
	_user = session.get('user')

	conn = mysql.connect()
	cursor = conn.cursor()
	query = "SELECT * FROM wish WHERE id = %s AND user_id = %s"
	parameter = (_id, _user)
	cursor.execute(query, parameter)
	data = cursor.fetchall()

	if len(data) > 0:
		return render_template('editWish.html', data = data)
	else:
		return render_template('error.html', error = "Wish not found!")

@app.route('/updateWish', methods = ['POST'])
def updateWish():
	_id = request.form['id']
	_title = request.form['title']
	_description = request.form['description']

	conn = mysql.connect()
	cursor = conn.cursor()
	query = "UPDATE wish SET title = %s, description = %s WHERE id = %s"
	parameter = (_title, _description, _id)
	cursor.execute(query, parameter)

	data = cursor.fetchall()
	if len(data) is 0:
		conn.commit()
		return redirect('/home')
	else:
		return render_template('error.html', error = "Update wish failed")

@app.route('/deleteWish', methods = ['POST'])
def deleteWish():
	_id = request.form['id']
	_user = session.get('user')

	conn = mysql.connect()
	cursor = conn.cursor()
	query = "SELECT * FROM wish WHERE id = %s AND user_id = %s"
	parameter = (_id, _user)
	cursor.execute(query, parameter)
	
	data = cursor.fetchall()
	if len(data) > 0:
		cursor.close()

		cursor = conn.cursor()
		query = "DELETE FROM wish WHERE id = %s AND user_id = %s"
		parameter = (_id, _user)
		cursor.execute(query, parameter)
		data = cursor.fetchall()
		if len(data) is 0:
			conn.commit()
			return redirect('/home')
		else:
			return render_template('error.html', error = "Failed to delete wish!")	
	else:
		return render_template('error.html', error = "Wish not found!")

@app.route('/checkWish', methods = ['POST'])
def checkWish():
	_id = request.form['id']
	_user = session.get('user')

	conn = mysql.connect()
	cursor = conn.cursor()
	query = "UPDATE wish SET status = 1 WHERE id = %s AND user_id = %s"
	parameter = (_id, _user)
	cursor.execute(query, parameter)

	data = cursor.fetchall()
	if len(data) is 0:
		conn.commit()
		return json.dumps({'message':'Wish checked!'})
	else:
		return json.dumps({'message':str(data[0])})


@app.route('/uncheckWish', methods = ['POST'])
def uncheckWish():
	_id = request.form['id']
	_user = session.get('user')

	conn = mysql.connect()
	cursor = conn.cursor()
	query = "UPDATE wish SET status = 0 WHERE id = %s AND user_id = %s"
	parameter = (_id, _user)
	cursor.execute(query, parameter)

	data = cursor.fetchall()
	if len(data) is 0:
		conn.commit()
		return json.dumps({'message':'Wish unchecked!'})
	else:
		return json.dumps({'message':str(data[0])})


@app.route('/getUncheckedWish')
def getUncheckedWish():
	conn = mysql.connect()
	cursor = conn.cursor()
	query = "SELECT * FROM wish WHERE user_id = %s AND status = 0"
	parameter = (session.get('user'))
	cursor.execute(query, parameter)
	data = cursor.fetchall()

	if len(data) > 0:
		uncheckedWish = []
		for wish in data:
			wishes = {
				'id': wish[0],
				'title':wish[1],
				'description':wish[2],
				'user_id':wish[3],
				'date':wish[4],
				'status':wish[5],
			}
			uncheckedWish.append(wishes)

		return json.dumps({'success':True, 'message':'Success get unchecked wish!', 'data':uncheckedWish})
	elif len(data) == 0:
		uncheckedWish = []
		return json.dumps({'success':True, 'message':'Success get unchecked wish!', 'data':uncheckedWish})
	else:
		return json.dumps({'success':False, 'message':'Failed get unchecked wish!'})

@app.route('/getCheckedWish')
def getCheckedWish():
	conn = mysql.connect()
	cursor = conn.cursor()
	query = "SELECT * FROM wish WHERE user_id = %s AND status = 1"
	parameter = (session.get('user'))
	cursor.execute(query, parameter)
	data = cursor.fetchall()

	if len(data) > 0:
		checkedWish = []
		for wish in data:
			wishes = {
				'id': wish[0],
				'title':wish[1],
				'description':wish[2],
				'user_id':wish[3],
				'date':wish[4],
				'status':wish[5],
			}
			checkedWish.append(wishes)

		return json.dumps({'success':True, 'message':'Success get checked wish!', 'data':checkedWish})
	elif len(data) == 0:
		checkedWish = []
		return json.dumps({'success':True, 'message':'Success get unchecked wish!', 'data':checkedWish})
	else:
		return json.dumps({'success':False, 'message':'Failed get checked wish!'})

	


# run application
if __name__ == "__main__":
	app.run(debug=True)