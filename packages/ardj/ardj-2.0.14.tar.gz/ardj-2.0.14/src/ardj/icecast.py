# encoding=utf-8

"""
Icecast gateway for ardj.

Runs icecast2 with a config file tweaked for ardj.
"""

import os

from ardj.util import get_config, edit_file, get_user_path, get_exec_path, run2, run3


DEFAULT_CONFIG = """<!--
This is the configuration file for icecast, your streaming server.
It is tweaked to work with ardj, the artificial DJ complex.
You can quickly access this file with the `ardj icecast-config' command.

By default this config file sets up two streams ("mount points"):

1) /music.mp3 - this is where your playlist plays.

2) /live.mp3 - this is where you broadcast live, your voice or other sounds.
When you start broadcasting to this mount point, all listeners connected to
/music.mp3 are AUTOMATICALLY moved to /live.mp3 and will hear your live
broadcast, without disconnect.  When you disconnect, they go back to /music.mp3
same way.

Broadcasting to /live.mp3 can be well scripted.  You can enable recording the
stream to a file (last-live-stream.mp3), execute a script when you start
broadcasting (e.g., to notify your Twitter followers) and one when you finish
(e.g., to post-process the recording and upload to your web site).  By default
this is commented out, see below (dump-file, etc).

To broadcast:

- connect to http://127.0.0.1:8000 (normally you'd use public visible DNS name)
- log in using password "ardj_source" (PLEASE CHANGE THIS)
- send your stream to /music.mp3 or /live.mp3

See <http://umonkey.net/ardj/icecast/> for details.

--><icecast>
    <limits>
        <clients>128</clients>
        <sources>3</sources>
        <threadpool>5</threadpool>
        <queue-size>524288</queue-size>
        <client-timeout>30</client-timeout>
        <header-timeout>15</header-timeout>
        <source-timeout>10</source-timeout>
        <burst-on-connect>1</burst-on-connect>
        <burst-size>131072</burst-size>
    </limits>

    <authentication>
        <!-- Sources log in with username 'source' -->
        <source-password>ardj_source</source-password>

        <!-- Admin logs in with the username given below -->
        <admin-user>admin</admin-user>
        <admin-password>ardj_admin</admin-password>
    </authentication>

    <listen-socket>
        <port>8000</port>
    </listen-socket>

    <mount>
        <mount-name>/music.mp3</mount-name>
        <password>ardj_source</password>
    </mount>

    <mount>
        <mount-name>/live.mp3</mount-name>
        <password>ardj_source</password>
        <fallback-mount>/music.mp3</fallback-mount>
        <fallback-override>1</fallback-override>
        <!--
        <dump-file>{HOME}/.ardj/dump/last-live-stream.mp3</dump-file>
        <on-connect>{HOME}/.ardj/on-live-connected</on-connect>
        <on-disconnect>{HOME}/.ardj/on-live-disconnected</on-disconnect>
        -->
    </mount>

    <paths>
        <basedir>/usr/share/icecast2</basedir>
        <logdir>{HOME}/.ardj</logdir>
        <webroot>/usr/share/icecast2/web</webroot>
        <adminroot>/usr/share/icecast2/admin</adminroot>
        <alias source="/" dest="/status.xsl"/>
    </paths>

    <logging>
        <accesslog>icecast2-access.log</accesslog>
        <errorlog>icecast2-error.log</errorlog>
        <loglevel>3</loglevel>
        <logsize>10000</logsize>
    </logging>
</icecast>
"""


def get_pid_path():
    return get_user_path("icecast2.pid")


def cmd_config(arg=None, *args):
    if arg == "help":
        print "Opens the config file in your text editor."
        exit(1)

    elif arg is not None:
        print "This command takes no argument."
        exit(1)

    edit_file(get_config("icecast2.xml", DEFAULT_CONFIG))


def cmd_run(arg=None, *args):
    if arg == "help":
        print "Runs icecast2 with an ardj-specific config file."
        print "The config file is created if necessary."
        print "You will see the file name and be able to edit it."
        exit(1)

    elif arg is not None:
        print "This command takes no argument."
        exit(1)

    exe = get_exec_path("icecast2")
    if not exe:
        print "Could not find icecast2 executable in PATH.  Please install."
        osname = os.uname()[3]
        if "Ubuntu" in osname:
            print "Example: sudo apt-get install icecast2"
        exit(1)

    config = get_config("icecast2.xml", DEFAULT_CONFIG)
    print "Running %s with config file %s -- edit if necessary, then restart." % (exe, config)

    ret = run3([exe, "-c", config])


def reload():
    send_signal(get_pid_path(), 1)  # HUP
