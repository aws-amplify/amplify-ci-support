import re

def replace_in_file(file_path: str, pattern: str, substitute: str):
    """
    Find the pattern in the file and substitute it.
    """
    # Read contents from file as a single string
    file_handle = open(file_path, 'r')
    file_string = file_handle.read()
    file_handle.close()
    file_string = (re.sub(pattern, substitute, file_string))

    # Write contents back to the file.
    file_handle = open(file_path, 'w+')
    file_handle.write(file_string)
    file_handle.close()