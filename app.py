from flask import *
import sqlite3 as sql
app = Flask(__name__)

with sql.connect('databases/users.db') as conn:
    conn.execute('CREATE TABLE IF NOT EXISTS users(username, password);')
with sql.connect('databases/posts.db') as conn:
    conn.execute('CREATE TABLE IF NOT EXISTS posts(post, title, categories, date);')

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

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    return render_template('upload.html')

@app.route('/uploaded', methods=['GET', 'POST'])
def uploaded():
    return render_template('admin.html', message='File uploaded')

@app.route('/test', methods=['GET', 'POST'])
def test():
    with sql.connect('databases/users.db') as conn:
        cur = conn.cursor()
        results = cur.execute('SELECT * FROM users;').fetchall()
    return str(results)

app.run(debug=True)
