def write_to_file(file_path, value):
    with open(file_path, 'a') as out:
        out.write(value + '\n')
