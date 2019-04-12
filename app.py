from flask import *
import sqlite3 as sql
import os

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
            results = cur.execute('SELECT username FROM users WHERE username==? AND password==?;', (username, password)).fetchone()
        if results == None:
            return render_template('login.html', error='Invalid credentials')
        else:
            session['user'] = username
            return redirect('/admin')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user' in session:
        return render_template('admin.html')
    else:
        return render_template('login.html')

@app.route('/createuser', methods=['GET', 'POST'])
def createuser():
    return render_template('createuser.html')

@app.route('/createduser', methods=['GET', 'POST'])
def createduser():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
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

@app.route('/users', methods=['GET', 'POST'])
def users():
    with sql.connect('databases/users.db') as conn:
        cur = conn.cursor()
        results = cur.execute('SELECT * FROM users;').fetchall()
    users = ''
    for i in results:
        users = users + '<a href="/edituser' + i[0] + '">' + i[0] + '</a><br>'
    return render_template('users.html', users=Markup(users))

@app.route('/edituser<username>')
def edituser(username):
    with sql.connect('databases/users.db') as conn:
        cur = conn.cursor()
        results = cur.execute('SELECT username FROM users WHERE username==?;', (username,)).fetchone()
    return render_template('user.html', username=results[0])

@app.route('/editedusername', methods=['GET', 'POST'])
def editedusername():
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

@app.route('/editedpassword', methods=['GET', 'POST'])
def editedpassword():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        newpass = request.form['newpass']
        with sql.connect('databases/users.db') as conn:
            cur = conn.cursor()
            results = cur.execute('SELECT * FROM users WHERE username==?;', (username,)).fetchall()
        with sql.connect('databases/users.db') as conn:
            cur = conn.cursor()
            cur.execute('UPDATE users SET password=? WHERE username==?', (newpass, username))
            conn.commit()
        return redirect('/admin')

@app.route('/deleteduser', methods=['GET', 'POST'])
def deleteduser():
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

@app.route('/createpost', methods=['GET', 'POST'])
def createpost():
    return render_template('createpost.html')

@app.route('/createdpost', methods=['GET', 'POST'])
def createdpost():
    title = request.form['title']
    categories = request.form['categories']
    if categories == '':
        categories = 'Uncategorised'
    text = request.form['text']
    summary = request.form['summary']
    if summary == '':
        summary = text[:text.find('\r\n')]
    with sql.connect('databases/posts.db') as conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO posts VALUES (?,?,?,?);', (title, categories, text, summary))
        conn.commit()
    return redirect('/admin')

@app.route('/posts', methods=['GET', 'POST'])
def posts():
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

@app.route('/editpost<title>')
def editpost(title):
    with sql.connect('databases/posts.db') as conn:
        cur = conn.cursor()
        results = cur.execute('SELECT * FROM posts WHERE title==?;', (title,)).fetchall()
    return render_template('post.html', title=results[0][0], categories=results[0][1], content=results[0][2], summary=results[0][3])

@app.route('/editedpost', methods=['GET', 'POST'])
def editedpost():
    if request.method == 'POST':
        title = request.form['title']
        categories = request.form['categories']
        text = request.form['text']
        summary = request.form['summary']
        if summary == '':
            if text.find('\r\n') != -1:
                summary = text[:text.find('\r\n')]
            else:
                summary = text
        with sql.connect('databases/posts.db') as conn:
            cur = conn.cursor()
            results = cur.execute('UPDATE posts SET text=?, categories=?, summary=? WHERE title==?;', (text, categories, summary, title))
            conn.commit()
        return redirect('/admin')

@app.route('/deletedpost', methods=['GET', 'POST'])
def deletedpost():
    if request.method == 'POST':
        title = request.form['title']
        with sql.connect('databases/posts.db') as conn:
            cur = conn.cursor()
            results = cur.execute('DELETE FROM posts WHERE title==?;', (title,))
            conn.commit()
        return redirect('/admin')

@app.route('/createpage', methods=['GET', 'POST'])
def createpage():
    return render_template('createpage.html')

@app.route('/createdpage', methods=['GET', 'POST'])
def createdpage():
    title = request.form['title']
    text = request.form['text']
    with sql.connect('databases/pages.db') as conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO pages VALUES (?,?);', (title, text))
        conn.commit()
    return redirect('/admin')

@app.route('/pages', methods=['GET', 'POST'])
def pages():
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

@app.route('/editpage<title>')
def editpage(title):
    with sql.connect('databases/pages.db') as conn:
        cur = conn.cursor()
        results = cur.execute('SELECT * FROM pages WHERE title==?;', (title,)).fetchall()
    return render_template('page.html', title=results[0][0], content=results[0][1])

@app.route('/editedpage', methods=['GET', 'POST'])
def editedpage():
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        with sql.connect('databases/pages.db') as conn:
            cur = conn.cursor()
            results = cur.execute('UPDATE pages SET text=? WHERE title==?;', (text, title))
            conn.commit()
        return redirect('/admin')

@app.route('/deletedpage', methods=['GET', 'POST'])
def deletedpage():
    if request.method == 'POST':
        title = request.form['title']
        with sql.connect('databases/pages.db') as conn:
            cur = conn.cursor()
            results = cur.execute('DELETE FROM pages WHERE title==?;', (title,))
            conn.commit()
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
    if method == 'POST':
        name = request.form['name']
        email = request.form['email']
        feedback = request.form['feedback']
        with sql.connect('databases/feedback.db') as conn:
            cur = conn.cursor()
            cur.execute('INSERT INTO feeback VALUES (?,?,?);', (name, email, feedback))
            conn.commit()
        return redirect('/')

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
        categories = '<p><strong>Categories: </strong>' + results[0][1] + '</p>'
        return render_template('content.html', title=results[0][0], content=Markup(categories + results[0][2]))

app.run(debug=True)
