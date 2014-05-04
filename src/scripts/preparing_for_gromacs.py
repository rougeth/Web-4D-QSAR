# coding: utf-8
from utils import remove_line, replace_line

# script: preparing files to molecular dynamics
#
# Following QuimComp (Química computacional aplicada a QSAR) instructions:
#     - 7.2 Dinâmica molecular usando o GROMACS


# Removing the line '#include "ffusernb.itp"' from the file ff_file_name.itp
remove_line('#include "ffusernb.itp"', '/tmp/itp_file')

# Replacing '#include "gaff_spce.itp"' to '#include "gaff tip3p.itp"' from the
# file file_name.top
replace_line('#include "gaff_spce.itp"', '#include "gaff tip3p.itp"',
             '/tmp/top_file')
