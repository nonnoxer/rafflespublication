import flask
from flask import render_template
app = flask.Flask(__name__)

@app.route('/')
def root():
    return render_template('index.html')

app.run(debug=True)
