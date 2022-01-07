import importlib
import logging
import subprocess

from watchdog.events import FileSystemEvent, PatternMatchingEventHandler
from watchdog.observers import Observer

from .xml import get_data_from_project_file


class Plugin():

    def load_module():
        """Loads the module declared in the xml project file.
        The module must have a get_count(files: list) -> int function"""
        project_type = get_data_from_project_file()['project-type']
        return importlib.import_module(f'squirrel.plugins.{project_type}')

    def get_files(path):
        """Find all files in path"""
        find_output = subprocess.run(
            f'find {path} -type f -not -path "*/[@.]*"',
            shell=True,
            capture_output=True,
            text=True
        )
        return find_output.stdout.strip().split('\n')


class Handler(PatternMatchingEventHandler):
    """Checks filesystem for added or modified files"""
    # List used to store modified and created files
    files = []

    def __init__(self, patterns):
        """Set the patterns for PatternMatchingEventHandler"""
        # 'patterns' is added in watch.py daemon(), set the file type(s) to look for
        # 'ignore_patterns' ignore hidden files, atleast on unix filesystems
        PatternMatchingEventHandler.__init__(
            self, patterns=patterns, ignore_patterns=['.*'], ignore_directories=True)

    def on_created(self, event):
        """Event is created, you can process it now"""
        # if statement to prevent 'files' to have more than one item of each file
        if event.src_path not in self.files:
            self.files.append(event.src_path)

    def on_modified(self, event):
        """Event is modified, you can process it now"""
        # if statement to prevent 'files' to have more than one item of each file
        if event.src_path not in self.files:
            self.files.append(event.src_path)
