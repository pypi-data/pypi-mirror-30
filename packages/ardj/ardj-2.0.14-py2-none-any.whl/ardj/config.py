# encoding=utf-8

"""
ardj configuration interface

Holds a copy of the config file (~/.ardj/ardj.yaml), reload when changed.
"""

import json
import os
import yaml

from ardj.log import *
from ardj.util import get_config, edit_file, get_user_path


DEFAULT_CONFIG = """# This is the main configuration file for ardj.
# If you have questions even after reading the comments, try reading
# the documentation at <http://umonkey.net/ardj/>
#
# If something doesn't work, write to <hex@umonkey.net>.

# Database type: sqlite, mysql.
database: sqlite

# MySQL config
#mysql_login: ardj
#mysql_password: ardj
#mysql_database: ardj
#mysql_debug: yes

# SQLite config
# This is the database where the runtime data is stored.
sqlite_database: {DATA}/database.sqlite

# This is where you put the music and jingles that ardj should play.
musicdir: {DATA}/music


# Specify how many recently played artists should be skipped when picking a
# random track.  For example, if this is set to 5, then 5 most recently played
# artists will be ignored.
#
# If ardj can't find new music to play, it will resort to playing a completely
# random track.  So, setting this value too high doesn't break the stream, but
# can effectively render some playlists empty, if they have less than specified
# artists.
dupes: 0


# Default labels for new files.
default_labels: [music, tagme]


# If you want to track programs, name a file which will hold the current
# program name.  Program name is the name of a playlist which has the non-empty
# "program" property.  When a track is picked from such playlist, program name
# is updated.  You can use this to display things on your web site, for example.
#program_name_file: {DATA}/public/current_ardj_program.txt

# If you want to run a script when program changes, specify its name here.
#program_name_handler: {DATA}/on-program-change

# If you want to save current track info to a file so that you could access
# it from your scripts or other programs, set file name her.
#dump_last_track: ~/tmp/last_track.json


# If you plan to use Jabber, uncomment this block and insert the correct values.
#jabber_id: "alice:secret@server.com"

# Here you can specify admin emails.  They have extra privileges when using
# jabber or the CLI console (ardj console).
jabber_admins:
- admin@example.com
- console

# Pomote most active users to admins.  You can define how many users from the
# top voters are promoted and how many days count.
#promote_voters: 10
#promote_voters_days: 14


# If you want to see how many users are currently listening to the stream, enable this.
# Set to "no" to disable counting listeners.
icecast_status_url: "http://127.0.0.1:8000/status-json.xsl"


# Uncomment this to disable voting (e.g., for database maintenance).
#enable_voting: no

# Comment out after the playlists are tuned and work well.
debug_playlist: yes


# The socket that the database server listens to.  On a typical installation
# you would use a local server, so no need to change anythint.  However, if for
# some reason you wish to move the database server outside, you can specify a
# different location.
#web_socket: 127.0.0.1:8080
"""


class Config(object):
    instance = None

    def __init__(self, path):
        self.path = path
        self.data = {}
        self.mtime = 0

    @classmethod
    def load(cls):
        if cls.instance is None:
            cls.instance = cls(get_user_path("config.yaml"))
        cls.instance.refresh()
        return cls.instance

    def refresh(self):
        if not os.path.exists(self.path):
            log_debug("config: file {} does not exist", self.path)
            return

        mtime = os.stat(self.path).st_mtime
        if mtime > self.mtime:
            with open(self.path, "rb") as f:
                if self.mtime:
                    log_debug("config: reloading")
                self.data = yaml.load(f.read())
            self.mtime = mtime

        return self

    @classmethod
    def get(cls, key, default=None):
        instance = cls.load()
        return instance.data.get(key, default)


def cmd_edit(arg=None, *args):
    if arg == "help":
        print "Edits the config file using your configured text editor."
        return

    elif arg is not None:
        print "This command takes no argument."
        exit(1)

    config = get_config("config.yaml", DEFAULT_CONFIG)
    edit_file(config)


def cmd_get(arg=None, default=None, *args):
    if not arg:
        print "Please specify parameter name to read."
        exit(1)

    if arg == "help":
        print "Prints the value of a config key."
        exit(1)

    value = get(arg, default)
    if value is not None:
        print value.encode("utf-8")


def get(key, default=None):
    """Returns the value of a key."""
    return Config.get(key, default)


def get_path(key, default=None):
    v = Config.get(key, default)
    if v:
        v = os.path.expanduser(v)
    return v
