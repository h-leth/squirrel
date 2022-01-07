import subprocess
import os

file_types = ['*.txt', '*.py']

def find_files(path, file_types):
    project_files = ''
    for i in file_types:
        s = f'-name "{i}" -o '
        project_files += s
    find_output = subprocess.run(
        f'find {path} -type f \( {project_files[:-3]} \) -not -path "*/[@.]*"',
        shell=True,
        capture_output=True,
        text=True
    )
    return find_output.stdout.strip().split('\n')


def get_files(path, file_types):
    files_tuple = tuple(i[1:] for i in file_types)
    project_files = []
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename.endswith(files_tuple) and not filename.startswith('.'):
                project_files.append(os.path.join(root, filename))
    return project_files
    
# get_files() is faster than find_files()