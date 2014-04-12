from flask import render_template
from qsar import app
from qsar.forms import GromacsFileUpload

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/gromacs-file-test')
def gromacs():
    gromacs_form = GromacsFileUpload();

    return render_template('gromacs_file_test.html',
        form = gromacs_form)

@app.route('/gromacs-file-test/upload', methods=['POST'])
def gromacs_upload():
    gromacs_form = GromacsFileUpload();

    if gromacs_form.validate_on_submit():
        return render_template('gromacs_file_test_upload.html',
            success=True)

    return render_template('gromacs_file_test_upload.html',
        success=False)