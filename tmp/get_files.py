import subprocess
import os
import glob


#def get_files(path, file_types):
#    find_output = subprocess.run(
#        f'find {path} -type f -name {}-not -path "*/[@.]*"',
#        shell=True,
#        capture_output=True,
#        text=True
#    )
#    return find_output.stdout.strip().split('\n')


file_types = ('.txt',)

def get_files(path, file_types):
    project_files = []
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename.endswith(file_types) and not filename.startswith('.'):
                project_files.append(os.path.join(root, filename))
    return project_files
    
