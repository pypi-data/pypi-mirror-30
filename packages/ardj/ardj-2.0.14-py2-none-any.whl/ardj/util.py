# encoding=utf-8

"""
ARDJ, an artificial DJ.

This module contains various utility functions.
"""

import os
import subprocess

from ardj import get_data_path


__all__ = ["run", "run2", "run3", "run_grab", "edit_file", "get_config", "get_user_path",
           "get_exec_path", "format_duration", "format_age"]


def run(command):
    from ardj.log import log_debug

    command = [utf(x) for x in command]
    log_debug('> {}', ' '.join(command))

    p = subprocess.Popen(command)
    p.wait()

    return p.returncode


def run_grab(command, stdin_data=None):
    from ardj.log import log_debug

    command = [utf(x) for x in command]
    log_debug('executing: {}', ' '.join(command))

    p = subprocess.Popen(command,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate(stdin_data)

    return p.returncode, out, err


def run_replace(command):
    os.execvp(command[0], command)
    exit(1)


def lower(s):
    if type(s) == str:
        s = s.decode('utf-8')
    return s.lower().replace(u'ё', u'е')


def ucmp(a, b):
    return cmp(lower(a), lower(b))


def in_list(a, lst):
    for i in lst:
        if not ucmp(i, a):
            return True
    return False


def skip_current_track():
    """Sends a skip request to the appropriate source client."""
    from ardj import ezstream, ices

    if ezstream.skip():
        return True
    if ices.skip():
        return True
    return False


def utf(s):
    if isinstance(s, unicode):
        return s.encode("utf-8")
    return str(s)


def deutf(s):
    if isinstance(s, str):
        return s.decode("utf-8")
    return unicode(s)


def edit_file(filename):
    editor = os.getenv("EDITOR", "editor")
    run_replace([editor, filename])


def get_config(name, defaults):
    config = get_user_path(name)

    if not os.path.exists(config):
        with open(config, "wb") as f:
            ardj = get_exec_path("ardj")
            data = defaults.format(HOME=os.getenv("HOME"),
                                   DATA=os.path.dirname(config),
                                   BIN=os.path.dirname(ardj))
            f.write(data)
            os.chmod(config, 0640)

        print "Wrote default config to %s, PLEASE EDIT." % config

    return config


def get_user_path(path):
    """
    Returns the name of a user local file.
    Creates the ~/.ardj folder and subfolders if necessary.
    """

    root = os.path.expanduser("~/.ardj")
    path = os.path.join(root, path)

    folder = os.path.dirname(path)
    if not os.path.exists(folder):
        os.makedirs(folder)

    return path


def get_exec_path(command):
    """Returns the full path of an executable, None if not in $PATH."""
    for folder in os.getenv("PATH").split(os.pathsep):
        path = os.path.join(folder, command)
        if os.path.exists(path):
            return path
    return None


def get_music_path(*parts):
    from ardj import config
    root = config.get_path("musicdir")
    return os.path.join(root, *parts)


def run2(command, pidfile):
    p = subprocess.Popen(command)

    with open(pidfile, "wb") as f:
        f.write(str(p.pid))

    p.wait()
    os.unlink(pidfile)

    return p.returncode


def run3(command):
    os.execv(command[0], command)


def send_signal(fn, sig):
    if not os.path.exists(fn):
        return False

    with open(fn, "rb") as f:
        pid = int(f.read())

        try:
            os.kill(pid, sig)
            return True
        except OSError, e:
            print "Could not send signal to %s -- error %s" % (fn, e)
            return False


def format_duration(duration):
    duration = int(duration)

    parts = ['%02u' % (duration % 60)]
    duration /= 60
    if duration:
        parts.insert(0, '%02u' % (duration % 60))
        duration /= 60
        if duration:
            parts.insert(0, str(duration))

    result = ':'.join(parts)

    if len(parts) > 1:
        result = result.lstrip('0')

    return result


def format_age(since, now=None):
    if not since:
        return "never"

    if not now:
        now = time.time()

    duration = int(now - since)
    return format_duration(duration) + " ago"
