from flask import *
import sqlite3 as sql
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

with sql.connect('databases/users.db') as conn:
    conn.execute('CREATE TABLE IF NOT EXISTS users(username, password);')
with sql.connect('databases/posts.db') as conn:
    conn.execute('CREATE TABLE IF NOT EXISTS posts(title, categories, text);')

@app.route('/', methods=['GET', 'POST'])
def root():
    return render_template('index.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
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
            return render_template('admin.html')

@app.route('/newuser', methods=['GET', 'POST'])
def newuser():
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
            return render_template('admin.html', message='User created')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')

@app.route('/mail', methods=['GET', 'POST'])
def mail():
    print('mailed')
    return render_template('index.html')

@app.route('/users', methods=['GET', 'POST'])
def delete():
    with sql.connect('databases/users.db') as conn:
        cur = conn.cursor()
        results = cur.execute('SELECT * FROM users;').fetchall()
    users = ''
    for i in results:
        users = users + '<a href="/user' + i[0] + '">' + i[0] + '</a><br>'
    return render_template('users.html', users=Markup(users))

@app.route('/editedusername', methods=['GET', 'POST'])
def editedusername():
    if request.method == 'POST':
        username = request.form['username']
        newname = request.form['newname']
        password = request.form['password']
        with sql.connect('databases/users.db') as conn:
            cur = conn.cursor()
            results = cur.execute('SELECT * FROM users WHERE username==?;', (username,)).fetchall()
        with sql.connect('databases/users.db') as conn:
            cur = conn.cursor()
            cur.execute('UPDATE users SET username=? WHERE username==?', (newname, username))
            conn.commit()
        return render_template('admin.html', message='User updated')

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
        return render_template('admin.html', message='User updated')

@app.route('/deleteduser', methods=['GET', 'POST'])
def deleteuser():
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
        return render_template('admin.html', message='User deleted')

@app.route('/create', methods=['GET', 'POST'])
def upload():
    return render_template('create.html')

@app.route('/created', methods=['GET', 'POST'])
def uploaded():
    title = request.form['title']
    categories = request.form['categories']
    if categories == '':
        categories = 'Uncategorised'
    text = request.form['text']
    with sql.connect('databases/posts.db') as conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO posts VALUES (?,?,?);', (title, categories, text))
        conn.commit()
    return render_template('admin.html', message='File uploaded')

@app.route('/files', methods=['GET', 'POST'])
def files():
    with sql.connect('databases/posts.db') as conn:
        cur = conn.cursor()
        results = cur.execute('SELECT * FROM posts;').fetchall()
    result = []
    for i in range(len(results)):
        result.append(results.pop())
    content = ''
    for i in result:
        content = content + '<a href="/edit' + i[0] + '">' + i[0] + '</a><br>'
    return render_template('files.html', content=Markup(content))

@app.route('/editedfile', methods=['GET', 'POST'])
def editedfile():
    if request.method == 'POST':
        title = request.form['title']
        categories = request.form['categories']
        text = request.form['text']
        with sql.connect('databases/posts.db') as conn:
            cur = conn.cursor()
            results = cur.execute('UPDATE posts SET text=?, categories=? WHERE title==?;', (text, categories, title))
            conn.commit()
        return render_template('admin.html', message='File edited')

@app.route('/deletedfile', methods=['GET', 'POST'])
def deletedfile():
    if request.method == 'POST':
        title = request.form['title']
        with sql.connect('databases/posts.db') as conn:
            cur = conn.cursor()
            results = cur.execute('DELETE FROM posts WHERE title==?;', (title,))
            conn.commit()
        return render_template('admin.html', message='File deleted')

@app.route('/about')
def about():
    return render_template('about.html')

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
        content = content + '<a href="/' + i[0] + '">' + i[0] + '</a><br>'
    return render_template('works.html', content=Markup(content))

@app.route('/test', methods=['GET', 'POST'])
def test():
    with sql.connect('databases/posts.db') as conn:
        cur = conn.cursor()
        results = cur.execute('SELECT * FROM posts;').fetchall()
    return str(results)

@app.route('/edit<title>')
def editFile(title):
    with sql.connect('databases/posts.db') as conn:
        cur = conn.cursor()
        results = cur.execute('SELECT * FROM posts WHERE title==?;', (title,)).fetchall()
    return render_template('file.html', title=results[0][0], categories=results[0][1], content=results[0][2])

@app.route('/user<username>')
def edituser(username):
    with sql.connect('databases/users.db') as conn:
        cur = conn.cursor()
        results = cur.execute('SELECT username FROM users WHERE username==?;', (username,)).fetchone()
    return render_template('user.html', username=results[0])

@app.route('/<title>')
def serveFile(title):
    with sql.connect('databases/posts.db') as conn:
        cur = conn.cursor()
        results = cur.execute('SELECT * FROM posts WHERE title==?;', (title,)).fetchall()
    if results == []:
        return render_template('content.html', title='Error', content='File does not exist')
    else:
        results[0] = list(results[0])
        results[0][2] = results[0][2].replace('\r\n', '<br>')
        return render_template('content.html', title=results[0][0], categories=results[0][1], content=Markup(results[0][2]))

app.run(debug=True)
