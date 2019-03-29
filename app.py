from flask import *
import sqlite3 as sql
app = Flask(__name__)

with sql.connect('databases/users.db') as conn:
    conn.execute('CREATE TABLE IF NOT EXISTS users(username, password);')
with sql.connect('databases/posts.db') as conn:
    conn.execute('CREATE TABLE IF NOT EXISTS posts(post, date);')

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
            return 'Error invalid credentials'
        else:
            return render_template('admin.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/mail', methods=['GET', 'POST'])
def mail():
    return render_template('index.html')

app.run(debug=True)
