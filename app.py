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
            return render_template('error.html', error='Invalid credentials')
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

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    return render_template('delete.html')

@app.route('/deleteuser', methods=['GET', 'POST'])
def deleteuser():
    if request.method == 'POST':
        username = request.form['username']
        with sql.connect('databases/users.db') as conn:
            cur = conn.cursor()
            results = cur.execute('SELECT username FROM users WHERE username==?;', (username,)).fetchone()
        if results == None:
            return render_template('error.html', error='User does not exist')
        if session['user'] == username:
            return render_template('error.html', error='Cannot delete yourself')
        with sql.connect('databases/users.db') as conn:
            cur = conn.cursor()
            results = cur.execute('DELETE FROM users WHERE username==?;', (username,))
            conn.commit()
        return render_template('admin.html', message='User deleted')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    return render_template('upload.html')

@app.route('/uploaded', methods=['GET', 'POST'])
def uploaded():
    title = request.form['title']
    categories = request.form['categories']
    text = request.form['text']
    with sql.connect('databases/posts.db') as conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO posts VALUES (?,?,?);', (title, categories, text))
        conn.commit()
    return render_template('admin.html', message='File uploaded')

@app.route('/deletefile', methods=['GET', 'POST'])
def deletefile():
    return render_template('deletefile.html')

@app.route('/deletedfile', methods=['GET', 'POST'])
def deletedfile():
    if request.method == 'POST':
        filename = request.form['filename']
        with sql.connect('databases/posts.db') as conn:
            cur = conn.cursor()
            results = cur.execute('SELECT title FROM posts WHERE title==?;', (filename,)).fetchone()
        if results == None:
            return render_template('error.html', error='File does not exist')
        with sql.connect('databases/posts.db') as conn:
            cur = conn.cursor()
            results = cur.execute('DELETE FROM posts WHERE title==?;', (filename,))
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

@app.route('/<title>')
def serveFile(title):
    with sql.connect('databases/posts.db') as conn:
        cur = conn.cursor()
        results = cur.execute('SELECT * FROM posts WHERE title==?;', (title,)).fetchall()
    if results == []:
        return render_template('content.html', title='Error', content='File does not exist')
    else:
        return render_template('content.html', title=results[0][0], content=results[0][2])

app.run(debug=True)
