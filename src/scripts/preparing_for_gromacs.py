# coding: utf-8
from utils import remove_line

# script: preparing files to molecular dynamics
#
# Following QuimComp (Química computacional aplicada a QSAR) instructions:
#     - 7.2 Dinâmica molecular usando o GROMACS


# Removing the line '#include "ffusernb.itp"' from the file ff_file_name.itp
remove_line('#include "ffusernb.itp"', '/tmp/ff_file')
