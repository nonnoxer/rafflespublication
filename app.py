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

@app.route('/', methods=['GET', 'POST'])
def root():
    with sql.connect('databases/posts.db') as conn:
        cur = conn.cursor()
        results = cur.execute('SELECT * FROM posts;').fetchall()
    result = []
    for i in range(3):
        if len(results) > 0:
            result.append(results.pop())
    content = ''
    for i in result:
        content = content + '<a href="/' + i[0] + '"><h2>' + i[0] + '</h2></a><p>' + i[3] + '</p><br>'
    return render_template('index.html', content=Markup(content))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
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

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user' in session:
        return render_template('admin.html')
    else:
        return render_template('login.html')

@app.route('/createuser', methods=['GET', 'POST'])
def createuser():
    if 'user' in session:
        return render_template('createuser.html')
    else:
        return render_template('login.html')

@app.route('/createduser', methods=['GET', 'POST'])
def createduser():
    if 'user' in session:
        if request.method == 'POST':
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
        return render_template('login.html')

@app.route('/users', methods=['GET', 'POST'])
def users():
    if 'user' in session:
        with sql.connect('databases/users.db') as conn:
            cur = conn.cursor()
            results = cur.execute('SELECT * FROM users;').fetchall()
        users = ''
        for i in results:
            users = users + '<a href="/edituser' + i[0] + '">' + i[0] + '</a><br>'
        return render_template('users.html', users=Markup(users))
    else:
        return render_template('login.html')

@app.route('/edituser<username>')
def edituser(username):
    if 'user' in session:
        with sql.connect('databases/users.db') as conn:
            cur = conn.cursor()
            results = cur.execute('SELECT username FROM users WHERE username==?;', (username,)).fetchone()
        return render_template('user.html', username=results[0])
    else:
        return render_template('login.html')

@app.route('/editedusername', methods=['GET', 'POST'])
def editedusername():
    if 'user' in session:
        if request.method == 'POST':
            username = request.form['username']
            newname = request.form['newname']
            with sql.connect('databases/users.db') as conn:
                cur = conn.cursor()
                results = cur.execute('SELECT * FROM users WHERE username==?;', (username,)).fetchall()
            with sql.connect('databases/users.db') as conn:
                cur = conn.cursor()
                cur.execute('UPDATE users SET username=? WHERE username==?', (newname, username))
                conn.commit()
            return redirect('/admin')
    else:
        return render_template('login.html')

@app.route('/editedpassword', methods=['GET', 'POST'])
def editedpassword():
    if 'user' in session:
        if request.method == 'POST':
            username = request.form['username']
            newpass = request.form['newpass']
            newpass = sha256_crypt.encrypt(newpass)
            with sql.connect('databases/users.db') as conn:
                cur = conn.cursor()
                results = cur.execute('SELECT * FROM users WHERE username==?;', (username,)).fetchall()
            with sql.connect('databases/users.db') as conn:
                cur = conn.cursor()
                cur.execute('UPDATE users SET password=? WHERE username==?', (newpass, username))
                conn.commit()
            return redirect('/admin')
    else:
        return render_template('login.html')

@app.route('/deleteduser', methods=['GET', 'POST'])
def deleteduser():
    if 'user' in session:
        if request.method == 'POST':
            username = request.form['username']
            with sql.connect('databases/users.db') as conn:
                cur = conn.cursor()
                results = cur.execute('SELECT username FROM users WHERE username==?;', (username,)).fetchone()
            if results == None:
                return render_template('error.html', error='User does not exist')
            with sql.connect('databases/users.db') as conn:
                cur = conn.cursor()
                results = cur.execute('DELETE FROM users WHERE username==?;', (username,))
                conn.commit()
            return redirect('/admin')
    else:
        return render_template('login.html')

@app.route('/createpost', methods=['GET', 'POST'])
def createpost():
    if 'user' in session:
        return render_template('createpost.html')
    else:
        return render_template('login.html')

@app.route('/createdpost', methods=['GET', 'POST'])
def createdpost():
    if 'user' in session:
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
        return render_template('login.html')

@app.route('/posts', methods=['GET', 'POST'])
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
            content = content + '<a href="/editpost' + i[0] + '">' + i[0] + '</a><br>'
        return render_template('posts.html', content=Markup(content))
    else:
        return render_template('login.html')

@app.route('/editpost<title>')
def editpost(title):
    if 'user' in session:
        with sql.connect('databases/posts.db') as conn:
            cur = conn.cursor()
            results = cur.execute('SELECT * FROM posts WHERE title==?;', (title,)).fetchall()
        return render_template('post.html', title=results[0][0], categories=results[0][1], content=results[0][2], summary=results[0][3])
    else:
        return render_template('login.html')

@app.route('/editedpost', methods=['GET', 'POST'])
def editedpost():
    if 'user' in session:
        if request.method == 'POST':
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
        return render_template('login.html')

@app.route('/deletedpost', methods=['GET', 'POST'])
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

@app.route('/createpage', methods=['GET', 'POST'])
def createpage():
    if 'user' in session:
        return render_template('createpage.html')
    else:
        return render_template('login.html')

@app.route('/createdpage', methods=['GET', 'POST'])
def createdpage():
    if 'user' in session:
        title = request.form['title']
        text = request.form['text']
        with sql.connect('databases/pages.db') as conn:
            cur = conn.cursor()
            cur.execute('INSERT INTO pages VALUES (?,?);', (title, text))
            conn.commit()
        return redirect('/admin')
    else:
        return render_template('login.html')

@app.route('/pages', methods=['GET', 'POST'])
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
            content = content + '<a href="/editpage' + i[0] + '">' + i[0] + '</a><br>'
        return render_template('pages.html', content=Markup(content))
    else:
        return render_template('login.html')

@app.route('/editpage<title>')
def editpage(title):
    if 'user' in session:
        with sql.connect('databases/pages.db') as conn:
            cur = conn.cursor()
            results = cur.execute('SELECT * FROM pages WHERE title==?;', (title,)).fetchall()
        return render_template('page.html', title=results[0][0], content=results[0][1])
    else:
        return render_template('login.html')

@app.route('/editedpage', methods=['GET', 'POST'])
def editedpage():
    if 'user' in session:
        if request.method == 'POST':
            title = request.form['title']
            text = request.form['text']
            with sql.connect('databases/pages.db') as conn:
                cur = conn.cursor()
                results = cur.execute('UPDATE pages SET text=? WHERE title==?;', (text, title))
                conn.commit()
            return redirect('/admin')
    else:
        return render_template('login.html')

@app.route('/deletedpage', methods=['GET', 'POST'])
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
    result = []
    for i in range(len(results)):
        result.append(results.pop())
    content = ''
    for i in result:
        content = content + '<a href="/' + i[0] + '"><h2>' + i[0] + '</h2></a><p>' + i[3] + '</p><br>'
    return render_template('content.html', title='Works', content=Markup(content))

@app.route('/categories')
def categories():
    with sql.connect('databases/posts.db') as conn:
        cur = conn.cursor()
        results = cur.execute('SELECT categories FROM posts;').fetchall()
    result = []
    for i in results:
        i = list(i)
        i[0] = i[0].split(',')
        for j in i[0]:
            j = j.strip()
            if j not in result:
                result.append(j)
    categories = ''
    for i in result:
        categories = categories + '<a href="/category' + i + '">' + i + '</a><br>'
    return render_template('content.html', title='Categories', content=Markup(categories))

@app.route('/category<category>')
def category(category):
    with sql.connect('databases/posts.db') as conn:
        cur = conn.cursor()
        results = cur.execute('SELECT * FROM posts;').fetchall()
    result = []
    content = ''
    for i in results:
        i = list(i)
        i[1] = i[1].split(',')
        for j in i[1]:
            if category in j:
                content = '<a href="/' + i[0] + '"><h2>' + i[0] + '</h2></a><p>' + i[3] + '</p><br>' + content
    return render_template('content.html', title=category, content=Markup(content))

@app.route('/all')
def other():
    content = '<a href="/">Home</a><br><a href="/About">About</a><br><a href="/works">Works</a><br><a href="/categories">Categories</a><br>'
    with sql.connect('databases/pages.db') as conn:
        cur = conn.cursor()
        results = cur.execute('SELECT * FROM pages').fetchall()
    for i in results:
        if i[0] != 'About':
            content = content + '<a href="/' + i[0] + '">' + i[0] + '</a><br>'
    return render_template('content.html', title='All Pages', content=Markup(content))

@app.route('/test', methods=['GET', 'POST'])
def test():
    with sql.connect('databases/posts.db') as conn:
        cur = conn.cursor()
        results = cur.execute('SELECT categories FROM posts;').fetchall()
    result = []
    for i in results:
        i = list(i)
        i[0] = i[0].split(',')
        for j in i[0]:
            if j not in result:
                result.append(j)
    return str(results)

@app.route('/feedback', methods=['GET', 'POST'])
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
    with sql.connect('databases/feedback.db') as conn:
        cur = conn.cursor()
        results = cur.execute('SELECT * FROM feedback;').fetchall()
    feedback = ''
    for i in results:
        feedback = feedback + "<tr><form action='deletedfeedback' method='POST' id='feedbacker'><td>" + i[0] + "</td><td>" + i[1] + "</td><td><textarea form='feedbacker' name='feedback' rows='4' readonly>" + i[2] + "</textarea></td><td><input type='submit' value='Delete'></form></tr>"
    return render_template('feedback.html', feedback=Markup(feedback))

@app.route('/deletedfeedback', methods=['GET', 'POST'])
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
    with sql.connect('databases/posts.db') as conn:
        cur = conn.cursor()
        results = cur.execute('SELECT * FROM posts WHERE title==?;', (title,)).fetchall()
    if results == []:
        with sql.connect('databases/pages.db') as conn:
            cur = conn.cursor()
            results = cur.execute('SELECT * FROM pages WHERE title==?;', (title,)).fetchall()
        if results == []:
            return render_template('content.html', title='Error', content='File does not exist')
        else:
            results[0] = list(results[0])
            results[0][1] = results[0][1].replace('\r\n', '<br>')
            return render_template('content.html', title=results[0][0], content=Markup(results[0][1]))
    else:
        results[0] = list(results[0])
        results[0][2] = results[0][2].replace('\r\n', '<br>')
        results[0][1] = results[0][1].split(',')
        categories = '<p><strong>Categories: </strong>'
        for i in results[0][1]:
            categories = categories + "<a href='/category" +  i + "'>" + i + '</a>, '
        categories = categories[:len(categories) - 2] + '</p>'
        return render_template('content.html', title=results[0][0], content=Markup(categories + results[0][2]))

app.run(debug=True)
