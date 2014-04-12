from flask import render_template
from qsar import app

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/gromacs-file-test')
def gromacs():
    return render_template('gromacs_file_test.html')