def remove_line(l, file):
    """Remove a line from a file

    :param l: line to be removed (str)
    :param file: file that the file will be removed (str)
    """
    with open(file, 'r') as f:
        lines = f.readlines()

    with open(file, 'w') as f:
        for line in lines:
            if line[:-1] != l:
                f.write(line)
