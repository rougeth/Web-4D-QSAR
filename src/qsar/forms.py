from flask.ext.wtf import Form
from wtforms import FileField
from wtforms.validators import DataRequired


class GromacsFileUpload(Form):
    gromacs_file = FileField('Gromacs File', validators=[DataRequired()])
