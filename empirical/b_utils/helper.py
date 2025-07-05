import os
import sys


# Storage file for utility functions that assist with different tasks
def get_directory_name(absolute_path):
    if absolute_path is None:
        raise TypeError(
            "absolute_path must be provided as argument for get_directory_name function"
        )
    directory_name, file_name = os.path.split(absolute_path)
    _, directory_name = os.path.split(directory_name)
    final_file_name = os.path.join(directory_name, file_name)

    return final_file_name


if __name__ == "__main__":
    pass
