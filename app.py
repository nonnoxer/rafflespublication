from flask import *
import sqlite3 as sql
import os
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.secret_key = os.urandom(24)

with sql.connect('databases/users.db') as conn:
	conn.execute('CREATE TABLE IF NOT EXISTS users(username, password);')
with sql.connect('databases/posts.db') as conn:
	conn.execute('CREATE TABLE IF NOT EXISTS posts(title, categories, text, summary);')
with sql.connect('databases/pages.db') as conn:
	conn.execute('CREATE TABLE IF NOT EXISTS pages(title, text);')
with sql.connect('databases/feedback.db') as conn:
	conn.execute('CREATE TABLE IF NOT EXISTS feedback(name, email, feedback);')


errorstring = "<div class='body' style='width:100%;'><b>404: File does not exist</b></div>"

@app.route('/', methods=['GET', 'POST'])
def root():
	with sql.connect('databases/posts.db') as conn:
		cur = conn.cursor()
		results = cur.execute('SELECT * FROM posts;').fetchall()
	result = []
	for i in range(5):
		if len(results) > 0:
			result.append(results.pop())
	content = ''
	for i in result:
		content = content + '<div style="margin: 15px 0px 15px 0px;"><a href="/post/' + i[0] + '"><h3>' + i[0] + '</h3></a><p>' + i[3] + '</p></div>'
	content = '''<div class='col-3 sidebar'>
					<div class="row">
						<h4>Hello there!</h4>
						<p>Welcome to the Raffles Publications website! This is where we post our articles as well as make announcements. Hope you enjoy your stay!</p>
					</div>
					<div class="row">
						<div style="margin: 0px;text-align: left;width: 100%;padding: 10px;">
						  <a class="rpubs_icon fa fa-facebook" href="https://www.facebook.com/Raffles-Publications-1437480963198257/"></a>
						  <a class="rpubs_icon fa fa-pinterest" href="#"></a>
						  <a class="rpubs_icon fa fa-youtube" href="#"></a>
						  <a class="rpubs_icon fa fa-instagram" href="#"></a>
						</div>
					</div>
					<div class="row" style="margin-bottom: 25px;">
						<a href='/categories' class='orange round'>Read by Categories</a>
					</div>
					<div class="row">
						<p>Feel free to drop some suggestions. We always welcome feedback.</p>
						<form style="width: 90%;" action='/feedback' method='POST' id='feedback'>
						  <input style="width: 100%;margin: 5px 0px;" type='text' name='name' placeholder='Name' class='orange form'>
						  <input style="width: 100%;margin: 5px 0px;" type='email' name='email' placeholder='Email' class='orange form'>
						  <textarea style="width: 100%;margin: 5px 0px;" form='feedback' name='feedback' placeholder='Your message' class='orange form' rows='3'></textarea>
						  <input style="margin: 5px;margin-top:0px;" type='submit' name='Submit' class='orange round'>
						</form>
					</div>
				</div>
				<div class='col-9 body'>
						<h1>Recent Posts</h1>''' + \
						content + \
						'''<a href='/works'>More >></a>
				</div>'''
	return render_template('content.html', content=Markup(content))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
	if request.method == "GET":
		if 'user' in session:
			return render_template('admin.html')
		else:
			return render_template('login.html')
	else:
		username = request.form['username']
		password = request.form['password']
		with sql.connect('databases/users.db') as conn:
			cur = conn.cursor()
			results = cur.execute('SELECT * FROM users WHERE username==?;', (username,)).fetchall()
		if results == []:
			return render_template('login.html', error='Invalid credentials')
		elif sha256_crypt.verify(password, results[0][1]):
			session['user'] = username
			return redirect('/admin')
		else:
			return render_template('login.html', error='Invalid credentials')

@app.route('/createuser', methods=['GET', 'POST'])
def createuser():
	if 'user' in session:
		if request.method == "GET":
			return render_template('createuser.html')
		else:
			username = request.form['username']
			password = request.form['password']
			password = sha256_crypt.encrypt(password)
			with sql.connect('databases/users.db') as conn:
				cur = conn.cursor()
				results = cur.execute('SELECT username FROM users WHERE username==? AND password==?;', (username,password)).fetchone()
			if results != None:
				return render_template('error.html', error='User already exists')
			else:
				with sql.connect('databases/users.db') as conn:
					cur = conn.cursor()
					cur.execute('INSERT INTO users VALUES (?,?);', (username, password))
					conn.commit()
				return redirect('/admin')

	else:
		if request.method == "GET":
			return render_template('login.html')
		else:
			return "Unauthorised Access"

@app.route('/users')
def users():
	if 'user' in session:
		with sql.connect('databases/users.db') as conn:
			cur = conn.cursor()
			results = cur.execute('SELECT * FROM users;').fetchall()
		users = ''
		for i in results:
			users = users + '<a href="/edituser/' + i[0] + '">' + i[0] + '</a><br>'
		return render_template('users.html', users=Markup(users))
	else:
		return render_template('login.html')

@app.route('/edituser/<username>')
def edituser(username):
	if 'user' in session:
		with sql.connect('databases/users.db') as conn:
			cur = conn.cursor()
			results = cur.execute('SELECT username FROM users WHERE username==?;', (username,)).fetchone()
		if results == None:
				return render_template('content.html', title='Error', content=Markup(errorstring))

		return render_template('user.html', username=results[0])
	else:
		return render_template('login.html')


@app.route('/editedusername', methods=['POST'])
def editedusername():
	if 'user' in session:
		username = request.form['username']
		newname = request.form['newname']
		
		with sql.connect('databases/users.db') as conn:
			cur = conn.cursor()
			cur.execute('UPDATE users SET username=? WHERE username==?', (newname, username))
			conn.commit()
		return redirect('/admin')
	else:
		return render_template('login.html')

@app.route('/editedpassword', methods=['POST'])
def editedpassword():
	if 'user' in session:
		
		username = request.form['username']
		newpass = request.form['newpass']
		newpass = sha256_crypt.encrypt(newpass)

		with sql.connect('databases/users.db') as conn:
			cur = conn.cursor()
			cur.execute('UPDATE users SET password=? WHERE username==?', (newpass, username))
			conn.commit()
		return redirect('/admin')
	else:
		return render_template('login.html')

@app.route('/deleteduser', methods=['POST'])
def deleteduser():
	if 'user' in session:
		username = request.form['username']
		with sql.connect('databases/users.db') as conn:
			cur = conn.cursor()
			results = cur.execute('DELETE FROM users WHERE username==?;', (username,))
			conn.commit()
		if session['user'] == username:
			return redirect("/logout")
		return redirect('/admin')
	else:
		return "Unauthorised Access"

@app.route('/createpost', methods=['GET', 'POST'])
def createpost():
	if 'user' in session:
		if request.method == "GET":
			return render_template('createpost.html')
		else:
			title = request.form['title']
			categories = request.form['categories']
			if categories == '':
				categories = 'Uncategorised'
			else:
				categories = categories.replace(' ,', ',')
				categories = categories.replace(', ', ',')
			text = request.form['text']
			summary = request.form['summary']
			with sql.connect('databases/posts.db') as conn:
				cur = conn.cursor()
				cur.execute('INSERT INTO posts VALUES (?,?,?,?);', (title, categories, text, summary))
				conn.commit()
			return redirect('/admin')
	else:
		if request.method == "GET":
			return render_template('login.html')
		else:
			return "Unauthorised Access"

@app.route('/posts')
def posts():
	if 'user' in session:
		with sql.connect('databases/posts.db') as conn:
			cur = conn.cursor()
			results = cur.execute('SELECT * FROM posts;').fetchall()
		result = []
		for i in range(len(results)):
			result.append(results.pop())
		content = ''
		for i in result:
			content = content + '<a href="/editpost/' + i[0] + '">' + i[0] + '</a><br>'
		return render_template('posts.html', content=Markup(content))
	else:
		return render_template('login.html')

@app.route('/editpost/<title>', methods=['GET', 'POST'])
def editpost(title):
	if 'user' in session:
		if request.method == "GET":
			with sql.connect('databases/posts.db') as conn:
				cur = conn.cursor()
				results = cur.execute('SELECT * FROM posts WHERE title==?;', (title,)).fetchall()
			if results == []:
				return render_template('content.html', title='Error', content=Markup(errorstring))

			return render_template('post.html', title=results[0][0], categories=results[0][1], content=results[0][2], summary=results[0][3])
		else:
			title = request.form['title']
			categories = request.form['categories']
			if categories == '':
				categories = 'Uncategorised'
			else:
				categories = categories.replace(' ,', ',')
				categories = categories.replace(', ', ',')

			text = request.form['text']
			summary = request.form['summary']
			with sql.connect('databases/posts.db') as conn:
				cur = conn.cursor()
				results = cur.execute('UPDATE posts SET text=?, categories=?, summary=? WHERE title==?;', (text, categories, summary, title))
				conn.commit()
			return redirect('/admin')

	else:
		if request.method == "GET":
			return render_template('login.html')
		else:
			return "Unauthorised Access"


@app.route('/deletedpost', methods=['POST'])
def deletedpost():
	if 'user' in session:
		if request.method == 'POST':
			title = request.form['title']
			with sql.connect('databases/posts.db') as conn:
				cur = conn.cursor()
				results = cur.execute('DELETE FROM posts WHERE title==?;', (title,))
				conn.commit()
			return redirect('/admin')
	else:
		return render_template('login.html')

@app.route('/createpage', methods=['GET','POST'])
def createpage():
	if 'user' in session:
		if request.method == 'GET':
			return render_template('createpage.html')
		else:
			title = request.form['title']
			text = request.form['text']
			with sql.connect('databases/pages.db') as conn:
				cur = conn.cursor()
				cur.execute('INSERT INTO pages VALUES (?,?);', (title, text))
				conn.commit()
			return redirect('/admin')
	else:
		if request.method == "GET":
			return render_template('login.html')
		else:
			return "Unauthorised Access"

@app.route('/pages')
def pages():
	if 'user' in session:
		with sql.connect('databases/pages.db') as conn:
			cur = conn.cursor()
			results = cur.execute('SELECT * FROM pages;').fetchall()
		result = []
		for i in range(len(results)):
			result.append(results.pop())
		content = ''
		for i in result:
			content = content + '<a href="/editpage/' + i[0] + '">' + i[0] + '</a><br>'
		return render_template('pages.html', content=Markup(content))
	else:
		return render_template('login.html')

@app.route('/editpage/<title>', methods=['GET','POST'])
def editpage(title):
	if 'user' in session:
		if request.method == "GET":
			with sql.connect('databases/pages.db') as conn:
				cur = conn.cursor()
				results = cur.execute('SELECT * FROM pages WHERE title==?;', (title,)).fetchall()
			if results == []:
				return render_template('content.html', title='Error', content=Markup(errorstring))

			return render_template('page.html', title=results[0][0], content=results[0][1])
		else:
			title = request.form['title']
			text = request.form['text']
			with sql.connect('databases/pages.db') as conn:
				cur = conn.cursor()
				results = cur.execute('UPDATE pages SET text=? WHERE title==?;', (text, title))
				conn.commit()
			return redirect('/admin')

	else:
		if request.method == "GET":
			return render_template('login.html')
		else:
			return "Unauthorised Access"


@app.route('/deletedpage', methods=['POST'])
def deletedpage():
	if 'user' in session:
		if request.method == 'POST':
			title = request.form['title']
			with sql.connect('databases/pages.db') as conn:
				cur = conn.cursor()
				results = cur.execute('DELETE FROM pages WHERE title==?;', (title,))
				conn.commit()
			return redirect('/admin')
	else:
		return render_template('login.html')

@app.route('/logout')
def logout():
	session.clear()
	return redirect('/admin')

@app.route('/works')
def works():
	with sql.connect('databases/posts.db') as conn:
		cur = conn.cursor()
		results = cur.execute('SELECT * FROM posts;').fetchall()
	
	content = ''
	for i in results:
		content = content + '<div style="margin: 15px 0px 15px 0px;"><a href="/post/' + i[0] + '"><h3>' + i[0] + '</h3></a><p>' + i[3] + '</p></div>'
	content = '''<div class='col-12 body'>
		<h1>''' + "Works" + '''</h1>
		<p>''' + content + '''</p>
	</div>'''
	return render_template('content.html', content=Markup(content))

@app.route('/categories')
def categories():
	with sql.connect('databases/posts.db') as conn:
		cur = conn.cursor()
		results = cur.execute('SELECT categories FROM posts;').fetchall()
	result = set()
	for i in results:
		listofcategs = i[0].split(',')
		for j in listofcategs:
			j = j.strip()
			result.add(j)
	categories = ''
	for i in result:
		categories = categories + '<a href="/category/' + i + '"><h4>' + i + '</h4></a>'
	content = '''<div class='col-12 body'>
		<h1>''' + "Categories" + '''</h1>
		''' + categories + '''
	</div>'''
	return render_template('content.html', content=Markup(content))

@app.route('/category/<category>')
def category(category):
	with sql.connect('databases/posts.db') as conn:
		cur = conn.cursor()
		results = cur.execute('SELECT * FROM posts;').fetchall()
	result = []
	content = ''
	for i in results:
		listofcategs = i[1].split(',')
		for j in listofcategs:
			if category in j:
				content = content + '<div style="margin: 15px 0px 15px 0px;"><a href="/post/' + i[0] + '"><h3>' + i[0] + '</h3></a><p>' + i[3] + '</p></div>'
	content = '''<div class='col-12 body'>
		<h1>''' + category + '''</h1>
		''' + content + '''
	</div>'''
	return render_template('content.html', content=Markup(content))

@app.route('/all')
def other():
	content = '''
		<a href="/"><h4>Home</h4></a>
		<a href="/About"><h4>About</h4></a>
		<a href="/works"><h4>Works</h4></a>
		<a href="/categories"><h4>Categories</h4></a>'''

	with sql.connect('databases/pages.db') as conn:
		cur = conn.cursor()
		results = cur.execute('SELECT * FROM pages').fetchall()
	for i in results:
		if i[0] != 'About':
			content = content + '<a href="/' + i[0] + '"><h4>' + i[0] + '</h4></a>'
	content = '''<div class='col-12 body'>
		<h1>''' + "All pages" + '''</h1>
		<p>''' + content + '''</p>
	</div>'''
	return render_template('content.html', content=Markup(content))

@app.route('/feedback', methods=['POST'])
def feedback():
	if request.method == 'POST':
		name = request.form['name']
		email = request.form['email']
		feedback = request.form['feedback']
		with sql.connect('databases/feedback.db') as conn:
			cur = conn.cursor()
			cur.execute('INSERT INTO feedback VALUES (?,?,?);', (name, email, feedback))
			conn.commit()
		return redirect('/')

@app.route('/feedbacked')
def feedbacked():
	if 'user' in session:
		with sql.connect('databases/feedback.db') as conn:
			cur = conn.cursor()
			results = cur.execute('SELECT * FROM feedback;').fetchall()
		feedback = ''
		for i in results:
			feedback = feedback + '<tr><form action="deletedfeedback" method="POST" id="feedbacker"><td>' + i[0] + '</td><td>' + i[1] + '</td><td><textarea form="feedbacker" name="feedback" rows="4" readonly>' + i[2] + '</textarea></td><td><input type="submit" value="Delete"></form></tr>'
		return render_template('feedback.html', feedback=Markup(feedback))
	else:
		return render_template('login.html')

@app.route('/deletedfeedback', methods=['POST'])
def deletedfeedback():
	if request.method == 'POST':
		feedback = request.form['feedback']
		with sql.connect('databases/feedback.db') as conn:
			cur = conn.cursor()
			cur.execute('DELETE FROM feedback WHERE feedback==?;', (feedback,))
			conn.commit()
		return redirect('/admin')

@app.route('/<title>')
def serveFile(title):
	with sql.connect('databases/pages.db') as conn:
		cur = conn.cursor()
		results = cur.execute('SELECT * FROM pages WHERE title==?;', (title,)).fetchall()
	if results == []:
		return render_template('content.html', title='Error', content=Markup(errorstring))
	else:
		results[0] = list(results[0])
		results[0][1] = results[0][1].replace('\r\n', '<br>')
		content = '''<div class='col-12 body'>
		  <h1>''' + results[0][0] + '''</h1></div>'''
		return render_template('viewcontent.html', content=Markup(content), posttext = Markup(results[0][1]))


@app.route('/post/<title>')
def servePost(title):
	with sql.connect('databases/posts.db') as conn:
		cur = conn.cursor()
		results = cur.execute('SELECT * FROM posts WHERE title==?;', (title,)).fetchall()
	if results == []:
		return render_template('content.html', title='Error', content=Markup(errorstring))
	else:
		results[0] = list(results[0])
		results[0][2] = results[0][2].replace('\r\n', '<br>')
		results[0][1] = results[0][1].split(',')
		categories = '<p><strong>Categories: </strong>'
		for i in results[0][1]:
			categories = categories + '<a href="/category' +  i + '">' + i + '</a>, '
		categories = categories[:len(categories) - 2] + '</p>'
		
		content = "<div class='col-12 body' style='padding-bottom:5px;'><h1>" + results[0][0] + "</h1><p>" + categories + "</p></div>"
		
		return render_template('viewcontent.html', content=Markup(content), posttext = Markup(results[0][2]))

app.run(debug=True)
