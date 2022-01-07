import os
import time
import functools
import signal
from datetime import datetime
import logging
from daemonize import Daemonize

from squirrel.plugin import Plugin, Handler, Observer
from ..vars import logger, watch_daemon_pidfile_path, watch_daemon_logfile_path, DAEMON_NAME, console
from ..xml import add_watch_entry


def watch(args):
    logger.debug(args)
    wd = os.getcwd()

    if args.daemon:
        daemon_logger, keep_fds = setup_daemon_logger()
        d = Daemonize(app=DAEMON_NAME,
                      pid=watch_daemon_pidfile_path,
                      action=functools.partial(daemon, wd, daemon_logger),
                      logger=daemon_logger,
                      keep_fds=keep_fds)
        d.start()
    else:
        try:
            daemon(wd, logger)
        except KeyboardInterrupt:
            pass


def status(args):
    logger.debug(args)
    pid = get_daemon_pid()
    if pid != 0:
        if pid_exists(pid):
            console.print('🟢 squirreld watcher is running')
        else:
            console.print('🔴 squirreld watcher is not running')
    else:
        console.print('🔴 squirreld watcher is not running')


def stop(args):
    logger.debug(args)
    pid = get_daemon_pid()
    os.kill(pid, signal.SIGTERM)
    console.print('Stopping squirreld watcher')


def pid_exists(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def get_daemon_pid() -> int:
    path = watch_daemon_pidfile_path
    try:
        with open(path, 'r') as f:
            pid = f.readline()
            return int(pid)
    except FileNotFoundError:
        return 0


def daemon(wd, logger):

    os.chdir(wd)
    watches = wd
    project_files = Plugin.get_files(wd)
    logger.info(f'{Plugin.get_files.__name__}: Project files intialized.')
    logger.info(
        f'{Plugin.get_files.__name__}: {len(project_files)} files found')
    engine = Plugin.load_module()

    # TODO?: Add filetype to project.xml? So it can be project spesific files
    # can be called from something like "engine.file_type"?
    file_type = ['*.txt']
    event_handler = Handler(patterns=file_type)
    observer = Observer()
    observer.schedule(event_handler, watches, recursive=True)
    observer.start()
    logger.debug('Watchdog initialized')
    while True:
        # If modified file found by Watchdog
        if event_handler.files:
            for file in event_handler.files:
                logger.info(f'Found a modified file {file.split("/")[-1]}')
                # Check if modified file exists in project_file list
                if file not in project_files:
                    project_files.append(file)
            # Counts files in project folder
            start = time.time()
            total = engine.get_count(project_files)
            end = time.time()
            count_timer = round(end - start, 3)
            logger.info(
                f'{engine.__name__}: get_count({len(project_files)} files) -> {total} took {count_timem r}')
            added = add_watch_entry(total, datetime.now())
            if added:
                logger.debug('A new watch entry was added')
            # Clears the list before a new loop starts
            event_handler.files.clear()
        time.sleep(15)


def setup_daemon_logger():
    daemon_logger = logging.getLogger(DAEMON_NAME)
    daemon_logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(watch_daemon_logfile_path)
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    daemon_logger.addHandler(fh)
    keep_fds = [fh.stream.fileno()]

    return daemon_logger, keep_fds
