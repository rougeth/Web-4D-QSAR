import os
from flask import request, render_template
from qsar import app
from werkzeug.utils import secure_filename


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/tests/gromacs-file-test', methods=['GET', 'POST'])
def gromacs_file_test():

    if request.method == 'POST':

        file = request.files['gromacs_file']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            return render_template('gromacs_file_test.html',
                success=True)

    return render_template('gromacs_file_test.html')