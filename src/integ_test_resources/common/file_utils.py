import os
import re


def replace_in_file(file_path: str, pattern: str, substitute: str) -> None:
    """
    Find the pattern in the file and substitute it.
    """
    if os.path.exists(file_path):
        # Read contents from file as a single string
        try:
            file_handle = open(file_path, "r")
            file_string = file_handle.read()
            file_handle.close()
        except OSError:
            raise IOError("Unable to read from specified file")

        file_string = re.sub(pattern, substitute, file_string)

        # Write contents back to the file.
        try:
            file_handle = open(file_path, "w+")
            file_handle.write(file_string)
            file_handle.close()
        except OSError:
            raise IOError("Unable to write to specified file")
    else:
        raise FileNotFoundError("Unable to find specified file")
