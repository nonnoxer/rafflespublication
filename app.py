from flask import *
import sqlite3 as sql
import os
from passlib.hash import sha256_crypt
from werkzeug.utils import secure_filename
import re
import html

app = Flask(__name__)
app.secret_key = os.urandom(24)

bigbigstring = os.path.dirname(os.path.realpath(__file__))

with sql.connect(os.path.join(bigbigstring,'databases/users.db')) as conn:
	conn.execute('CREATE TABLE IF NOT EXISTS users(username, password);')
with sql.connect(os.path.join(bigbigstring,'databases/posts.db')) as conn:
	conn.execute('CREATE TABLE IF NOT EXISTS posts(title, categories, text, summary, icon);')
with sql.connect(os.path.join(bigbigstring,'databases/pages.db')) as conn:
	conn.execute('CREATE TABLE IF NOT EXISTS pages(title, text);')
with sql.connect(os.path.join(bigbigstring,'databases/feedback.db')) as conn:
	conn.execute('CREATE TABLE IF NOT EXISTS feedback(name, email, feedback);')

errorstring = "<div class='body' style='width:100%;'><b>404: File does not exist</b></div>"

def qntosafe(mystring):
	if "?" in mystring:
		mystring = mystring.replace("?", "--qn--")
	mystring = html.escape(mystring)
	return mystring

def safetoqn(mystring):
	if "-qn-" in mystring:
		mystring = mystring.replace("--qn--", "?")
	#mystring = html.unescape(mystring)
	return mystring


@app.route('/', methods=['GET', 'POST'])
def root():
	with sql.connect(os.path.join(bigbigstring,'databases/posts.db')) as conn:
		cur = conn.cursor()
		results = cur.execute('SELECT * FROM posts;').fetchall()
	result = []
	for i in range(5):
		if len(results) > 0:
			result.append(results.pop())
	content = ''
	for i in result:
		content = content + '''<div class="container">
			<div class="row">
				<div class="col-3" style="text-align: center;">
					<img src="/static/files/''' + i[4] + '''" class="icon">
				</div>
				<div style="margin: 15px 0px 15px 0px;" class="col-9">
					<a href="/post/''' + i[0] + '''">
						<h3>''' + qntosafe(i[0]) + '''</h3>
					</a>
					<p>''' + i[3] + '''</p>
				</div>
			</div>
		</div>'''
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
		with sql.connect(os.path.join(bigbigstring,'databases/users.db')) as conn:
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
			with sql.connect(os.path.join(bigbigstring,'databases/users.db')) as conn:
				cur = conn.cursor()
				results = cur.execute('SELECT username FROM users WHERE username==? AND password==?;', (username,password)).fetchone()
			if results != None:
				return render_template('error.html', error='User already exists')
			else:
				with sql.connect(os.path.join(bigbigstring,'databases/users.db')) as conn:
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
		with sql.connect(os.path.join(bigbigstring,'databases/users.db')) as conn:
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
		with sql.connect(os.path.join(bigbigstring,'databases/users.db')) as conn:
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

		with sql.connect(os.path.join(bigbigstring,'databases/users.db')) as conn:
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

		with sql.connect(os.path.join(bigbigstring,'databases/users.db')) as conn:
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
		with sql.connect(os.path.join(bigbigstring,'databases/users.db')) as conn:
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
			title = qntosafe(request.form['title'])
			categories = request.form['categories']
			if categories == '':
				categories = 'Uncategorised'
			else:
				categories = categories.replace(' ,', ',')
				categories = categories.replace(', ', ',')
			text = request.form['text']
			summary = request.form['summary']

			#print(request.files)
			#print(request.form)
			if 'icon' in request.form and request.form['icon'] == "":
				filename = 'default.png'

			##Error code!!
			#if str(request.files['icon']) == "<FileStorage: '' ('application/octet-stream')>":
				#filename = 'default.png'
			else:
				f = open(os.path.join(bigbigstring,'databases/config.txt'), 'r')
				f = f.readlines()
				fname = f[0].strip()
				fname = str(fname)
				icon = request.files['icon']
				filename = fname + icon.filename[icon.filename.find('.'):]
				icon.save(os.path.join(bigbigstring, 'static', 'files', secure_filename(filename)))
				f = open(os.path.join(bigbigstring,'databases/config.txt'), 'w')
				f.write(str(int(fname) + 1))
				f.close()
			
			categories = html.escape(categories)
			summary = html.escape(summary)

			with sql.connect(os.path.join(bigbigstring,'databases/posts.db')) as conn:
				cur = conn.cursor()
				cur.execute('INSERT INTO posts VALUES (?,?,?,?,?);', (title, categories, text, summary, filename))
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
		with sql.connect(os.path.join(bigbigstring,'databases/posts.db')) as conn:
			cur = conn.cursor()
			results = cur.execute('SELECT * FROM posts;').fetchall()
		result = []
		for i in range(len(results)):
			result.append(results.pop())
		content = ''
		for i in result:
			content = content + '<a href="/editpost/' + i[0] + '">' + safetoqn(i[0]) + '</a><br>'
		return render_template('posts.html', content=Markup(content))
	else:
		return render_template('login.html')

@app.route('/editpost/<title>', methods=['GET', 'POST'])
def editpost(title):
	if 'user' in session:
		if request.method == "GET":
			with sql.connect(os.path.join(bigbigstring,'databases/posts.db')) as conn:
				cur = conn.cursor()
				results = cur.execute('SELECT * FROM posts WHERE title==?;', (title,)).fetchall()
			if results == []:
				return render_template('content.html', title='Error', content=Markup(errorstring))

			return render_template('post.html', title=results[0][0], title2 = safetoqn(results[0][0]), categories=results[0][1], content=results[0][2], summary=results[0][3], icon=results[0][4])
		else:
			title = qntosafe(request.form['title'])
			categories = request.form['categories']
			if categories == '':
				categories = 'Uncategorised'
			else:
				categories = categories.replace(' ,', ',')
				categories = categories.replace(', ', ',')

			text = request.form['text']
			summary = request.form['summary']
			f = open(os.path.join(bigbigstring,'databases/config.txt'), 'r')
			f = f.readlines()
			fname = f[0].strip()
			fname = str(fname)

			if 'icon' in request.form and request.form['icon'] == "":
				#blank no change to icon
				with sql.connect(os.path.join(bigbigstring,'databases/posts.db')) as conn:
					cur = conn.cursor()
					cur.execute('UPDATE posts SET text=?, categories=?, summary=? WHERE title==?;', (text, categories, summary, title))
					conn.commit()
			else:
				icon = request.files['icon']
				filename = fname + icon.filename[icon.filename.find('.'):]
				icon.save(os.path.join(bigbigstring, 'static', 'files', secure_filename(filename)))
				f = open(os.path.join(bigbigstring,'databases/config.txt'), 'w')
				f.write(str(int(fname) + 1))
				f.close()
				with sql.connect(os.path.join(bigbigstring,'databases/posts.db')) as conn:
					cur = conn.cursor()
					results = cur.execute('SELECT icon FROM posts WHERE title==?;', (title,)).fetchone()
				if results[0] != 'default.png':
					os.remove(os.path.join(bigbigstring, 'static', 'files', results[0]))
				with sql.connect(os.path.join(bigbigstring,'databases/posts.db')) as conn:
					cur = conn.cursor()
					cur.execute('UPDATE posts SET text=?, categories=?, summary=?, icon=? WHERE title==?;', (text, categories, summary, filename, title))
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
			title = qntosafe(request.form['title'])
			with sql.connect(os.path.join(bigbigstring,'databases/posts.db')) as conn:
				cur = conn.cursor()

				results = cur.execute('SELECT icon FROM posts WHERE title==?;', (title,)).fetchone()
				if results[0] != 'default.png':
					os.remove(os.path.join(bigbigstring, 'static', 'files', results[0]))

				cur.execute('DELETE FROM posts WHERE title==?;', (title,))
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
			title = qntosafe(request.form['title'])
			text = request.form['text']
			with sql.connect(os.path.join(bigbigstring,'databases/pages.db')) as conn:
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
		with sql.connect(os.path.join(bigbigstring,'databases/pages.db')) as conn:
			cur = conn.cursor()
			results = cur.execute('SELECT * FROM pages;').fetchall()
		result = []
		for i in range(len(results)):
			result.append(results.pop())
		content = ''
		for i in result:
			content = content + '<a href="/editpage/' + i[0] + '">' + safetoqn(i[0]) + '</a><br>'
		return render_template('pages.html', content=Markup(content))
	else:
		return render_template('login.html')

@app.route('/editpage/<title>', methods=['GET','POST'])
def editpage(title):
	if 'user' in session:
		if request.method == "GET":
			with sql.connect(os.path.join(bigbigstring,'databases/pages.db')) as conn:
				cur = conn.cursor()
				results = cur.execute('SELECT * FROM pages WHERE title==?;', (title,)).fetchall()
			if results == []:
				return render_template('content.html', title='Error', content=Markup(errorstring))

			return render_template('page.html', title=results[0][0], title2 = safetoqn(results[0][0]), content=results[0][1])
		else:
			title = qntosafe(request.form['title'])
			text = request.form['text']
			with sql.connect(os.path.join(bigbigstring,'databases/pages.db')) as conn:
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
			title = qntosafe(request.form['title'])
			with sql.connect(os.path.join(bigbigstring,'databases/pages.db')) as conn:
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
	with sql.connect(os.path.join(bigbigstring,'databases/posts.db')) as conn:
		cur = conn.cursor()
		results = cur.execute('SELECT * FROM posts;').fetchall()

	content = ''
	for i in results:
		content ='''<div class="container">
			<div class="row">
				<div class="col-2" style="text-align: center;">
					<img src="/static/files/''' + i[4] + '''" class="icon">
				</div>
				<div style="margin: 15px 0px 15px 0px;" class="col-10">
					<a href="/post/''' + i[0] + '''">
						<h3>''' + safetoqn(i[0]) + '''</h3>
					</a>
					<p>''' + i[3] + '''</p>
				</div>
			</div>
		</div>''' + content
	content = '''<div class='col-12 body'>
		<h1>''' + "Works" + '''</h1>
		<p>''' + content + '''</p>
	</div>'''
	return render_template('content.html', content=Markup(content))

@app.route('/categories')
def categories():
	with sql.connect(os.path.join(bigbigstring,'databases/posts.db')) as conn:
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
	with sql.connect(os.path.join(bigbigstring,'databases/posts.db')) as conn:
		cur = conn.cursor()
		results = cur.execute('SELECT * FROM posts;').fetchall()
	result = []
	content = ''
	for i in results:
		listofcategs = i[1].split(',')
		for j in listofcategs:
			if category in j:
				content = '''<div class="container">
					<div class="row">
						<div class="col-2" style="text-align: center;">
							<img src="/static/files/''' + i[4] + '''" class="icon">
						</div>
						<div style="margin: 15px 0px 15px 0px;" class="col-10">
							<a href="/post/''' + i[0] + '''">
								<h3>''' + safetoqn(i[0]) + '''</h3>
							</a>
							<p>''' + i[3] + '''</p>
						</div>
					</div>
				</div>''' + content
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

	with sql.connect(os.path.join(bigbigstring,'databases/pages.db')) as conn:
		cur = conn.cursor()
		results = cur.execute('SELECT * FROM pages').fetchall()
	for i in results:
		if i[0] != 'About':
			content = content + '<a href="/' + i[0] + '"><h4>' + safetoqn(i[0]) + '</h4></a>'
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
		with sql.connect(os.path.join(bigbigstring,'databases/feedback.db')) as conn:
			cur = conn.cursor()
			cur.execute('INSERT INTO feedback VALUES (?,?,?);', (name, email, feedback))
			conn.commit()
		return redirect('/')

@app.route('/feedbacked')
def feedbacked():
	if 'user' in session:
		with sql.connect(os.path.join(bigbigstring,'databases/feedback.db')) as conn:
			cur = conn.cursor()
			results = cur.execute('SELECT * FROM feedback;').fetchall()
		feedback = ''
		for i in results:
			feedback = feedback + '<tr><form action="/deletedfeedback" method="POST" id="feedbacker"><td>' + i[0] + '</td><td>' + i[1] + '</td><td><input name="feedback" value="' + i[2] + '" hidden readOnly>' + i[2] + '</td><td class="bigdelete"> \
			<center><button form="feedbacker" type="submit" class="btn btn-outline-danger">Delete</button></center></td></form></tr>'
		return render_template('feedback.html', feedback=Markup(feedback))
	else:
		return render_template('login.html')

@app.route('/deletedfeedback', methods=['POST'])
def deletedfeedback():
	if request.method == 'POST':
		feedback = request.form['feedback']
		print(feedback)
		with sql.connect(os.path.join(bigbigstring,'databases/feedback.db')) as conn:
			cur = conn.cursor()
			cur.execute('DELETE FROM feedback WHERE feedback==?;', (feedback,))
			conn.commit()
		return redirect('/admin')

@app.route('/search', methods=['POST'])
def search():
	if request.method == 'POST':
		search = qntosafe(request.form['search'])
		with sql.connect(os.path.join(bigbigstring,'databases/posts.db')) as conn:
			cur = conn.cursor()
			result = cur.execute('SELECT title, categories FROM posts').fetchall()

		with sql.connect(os.path.join(bigbigstring,'databases/pages.db')) as conn:
			cur = conn.cursor()
			result2 = cur.execute('SELECT title FROM pages').fetchall()

		results = []
		categore = []
		pagelist = []

		content = ''
		cattent = ''
		pagetent = ''

		for i in result:
			if re.search(search.lower(), i[0].lower()):
				results.append(i[0])
			if re.search(search.lower(), i[1].lower()) and i[1] not in categore:
				categore.append(i[1])

		for i in result2:
			if re.search(search.lower(), i[0].lower()):
				pagelist.append(i[0])


		if results == [] and categore == [] and pagelist == []:
			content = "Nothing here, sorry!"
			cattent = "Nothing here, sorry!"
			pagetent = "Nothing here, sorry!"
		else:
			if results !=[]:
				for i in results:
					with sql.connect(os.path.join(bigbigstring,'databases/posts.db')) as conn:
						cur = conn.cursor()
						result = cur.execute('SELECT * FROM posts WHERE title==?;', (i,)).fetchall()
					content ='''<div class="container">
						<div class="row">
							<div class="col-2" style="text-align: center;">
								<img src="/static/files/''' + result[0][4] + '''" class="icon">
							</div>
							<div style="margin: 15px 0px 15px 0px;" class="col-10">
								<a href="/post/''' + result[0][0] + '''">
									<h3>''' + safetoqn(result[0][0]) + '''</h3>
								</a>
								<p>''' + result[0][3] + '''</p>
							</div>
						</div>
					</div>''' + content
			else:
				content = "Nothing here, sorry!"

			if categore != []:
				for i in categore:
					cattent = '<a href="/category/' + i + '">' + i + '</a>' + cattent
			else:
				cattent = 'Nothing here, sorry!'

			if pagelist != []:
				for i in pagelist:
					pagetent = '''<div class="container">
						<div class="row">
							<div style="margin: 15px 0px 15px 0px;" class="col-12">
								<a href="/''' + i + '''">
									<h3>''' + safetoqn(i) + '''</h3>
								</a>
							</div>
						</div>
					</div>''' + pagetent
			else:
				pagetent = 'Nothing here, sorry!'

		content = '''<div class='col-12 body'>
				<h1>Search</h1>
				<form action='/search' method='POST'>
					<input type='text' name='search' placeholder='Search...' value="''' + search + '''">
					<button type='submit' style='background: None; border: None;'><i class="fa fa-search"></i></button>
				</form>
			</div>
			<div class="col-12 body">
				<h3>Posts</h3>
				<p>''' + content + '''</p>
			</div>
			<div class="col-12 body">
				<h3>Categories</h3>
				<p>''' + cattent + '''</p>
			</div>
			<div class="col-12 body">
				<h3>Pages</h3>
				<p>''' + pagetent + '''</p>
			</div>
			'''

		return render_template('content.html', content=Markup(content))

@app.route('/<title>')
def serveFile(title):
	with sql.connect(os.path.join(bigbigstring,'databases/pages.db')) as conn:
		cur = conn.cursor()
		results = cur.execute('SELECT * FROM pages WHERE title==?;', (title,)).fetchall()
	if results == []:
		return render_template('content.html', title='Error', content=Markup(errorstring))
	else:
		results = list(results[0])
		#results[1] = results[1].replace('\r\n', '<br>')
		content = '''
		<div class='col-12 body'>
		  <h1>''' + safetoqn(results[0]) + '''</h1>
		</div>
		<div id="editor" style="width: 100%;background-color: white;"></div>

		<p id="datasource" style="display: none;">''' + results[1] + '''</p>

		<script type="text/javascript">
			var quill = new Quill('#editor', {
			theme: 'bubble',
			"modules": {
				"toolbar": false,
			},
			readOnly: true,
			});
			mystring = document.getElementById("datasource").textContent;
			var mydelta = JSON.parse(mystring);
			var deltaOps =  mydelta["ops"];
			quill.setContents(deltaOps);

		</script>'''
		return render_template('content.html', content=Markup(content))
		#return str(results)

@app.route('/post/<title>')
def servePost(title):
	with sql.connect(os.path.join(bigbigstring,'databases/posts.db')) as conn:
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
			categories = categories + '<a href="/category/' +  i + '">' + i + '</a>, '
		categories = categories[:len(categories) - 2] + '</p>'

		content = "<div class='col-12 body' style='padding-bottom:5px;'><h1><img src='/static/files/" + results[0][4] + "' class='icon'>" + safetoqn(results[0][0]) + "</h1><p>" + categories + '''</p></div>

		<div id="editor" style="width: 100%;background-color: white;"></div>

		<p id="datasource" style="display: none;">''' + results[0][2] + '''</p>
		<script type="text/javascript">
			var quill = new Quill('#editor', {
			theme: 'bubble',
			"modules": {
				"toolbar": false,
			},
			readOnly: true,
			});
			mystring = document.getElementById("datasource").textContent;
			var mydelta = JSON.parse(mystring);
			var deltaOps =  mydelta["ops"];
			quill.setContents(deltaOps);
		</script>'''
		return render_template('content.html', content=Markup(content))

@app.route('/test')
def test():
	pass

@app.route('/print/<mode>')
def myprint(mode):
	if mode == "posts":
		with sql.connect(os.path.join(bigbigstring,'databases/posts.db')) as conn:
			cur = conn.cursor()
			results = cur.execute("SELECT * FROM posts").fetchall()

		return str(results[0])

	elif mode == "pages":
		with sql.connect(os.path.join(bigbigstring,'databases/pages.db')) as conn:
			cur = conn.cursor()
			results = cur.execute("SELECT * FROM pages").fetchall()
			
		return str(results)


if __name__ == "__main__":
	app.run(debug=False)
