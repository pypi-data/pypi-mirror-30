# encoding=utf-8

"""
Ices0 support for ardj.

Ices0 is a playlist server for icecast2.  It's currently replaced with ezstream
in most distros, and not without a reason, BUT it supports cross-fade!
Ezstream doesn't.  This sucks, to have a radio with no cross-fade.  You will
have to compile ices0 from sources, which is quite easy actually.  Latest
version patched to support replaygain is available here:

https://bitbucket.org/umonkey/ices0

When you have it running, run it with `ardj loop ices',
instead of `ardj loop ezstream'.
"""

import os

from ardj.log import *
from ardj.tracks import get_track_to_play_next
from ardj.util import get_config, edit_file, get_exec_path, get_user_path, run2, run3, send_signal


__all__ = [
    "ices_init",
    "ices_shutdown",
    "ices_get_next",
    "ices_get_metadata",
]


DEFAULT_CONFIG = """<?xml version="1.0"?>
<ices:Configuration xmlns:ices="http://www.icecast.org/projects/ices">
  <Playlist>
    <Randomize>0</Randomize>
    <Type>python</Type>
    <Module>ardj.ices</Module>
    <Crossfade>5</Crossfade>
  </Playlist>

  <Execution>
    <Background>0</Background>
    <Verbose>1</Verbose>
    <BaseDirectory>{DATA}</BaseDirectory>
  </Execution>

  <Stream>
    <Server>
      <!-- Hostname or ip of the icecast server you want to connect to -->
      <Hostname>localhost</Hostname>
      <!-- Port of the same -->
      <Port>8000</Port>
      <!-- Encoder password on the icecast server -->
      <Password>ardj_source</Password>
      <!-- Header protocol to use when communicating with the server.
           Shoutcast servers need "icy", icecast 1.x needs "xaudiocast", and
       icecast 2.x needs "http". -->
      <Protocol>http</Protocol>
    </Server>

    <!-- The name of the mountpoint on the icecast server -->
    <Mountpoint>/music.mp3</Mountpoint>
    <!-- The name of the dumpfile on the server for your stream. DO NOT set
     this unless you know what you're doing.
    <Dumpfile>ices.dump</Dumpfile>
    -->
    <!-- The name of you stream, not the name of the song! -->
    <Name>Default stream</Name>
    <!-- Genre of your stream, be it rock or pop or whatever -->
    <Genre>Default genre</Genre>
    <!-- Longer description of your stream -->
    <Description>Default description</Description>
    <!-- URL to a page describing your stream -->
    <URL>http://localhost/</URL>
    <!-- 0 if you don't want the icecast server to publish your stream on
     the yp server, 1 if you do -->
    <Public>0</Public>

    <!-- Stream bitrate, used to specify bitrate if reencoding, otherwise
     just used for display on YP and on the server. Try to keep it
     accurate -->
    <Bitrate>128</Bitrate>
    <!-- If this is set to 1, and ices is compiled with liblame support,
     ices will reencode the stream on the fly to the stream bitrate. -->
    <Reencode>1</Reencode>
    <!-- Number of channels to reencode to, 1 for mono or 2 for stereo -->
    <!-- Sampe rate to reencode to in Hz. Leave out for LAME's best choice
    <Samplerate>44100</Samplerate>
    -->
    <Channels>2</Channels>
  </Stream>
</ices:Configuration>
"""


songnumber = -1
last_track = None
last_good_file = None


def ices_init():
    """
    Function called to initialize your Python environment.
    Should return 1 if ok, and 0 if something went wrong.
    """
    log_info('Initializing.')
    return 1


def ices_shutdown():
    """
    Function called to shutdown your Python enviroment.
    Return 1 if ok, 0 if something went wrong.
    """
    log_info('Shutting down.')
    return 1


def ices_get_next():
    """
    Function called to get the next filename to stream.
    Should return a string.
    """
    global last_track, last_good_file

    last_track = get_track_to_play_next()

    if last_track and os.path.exists(last_track["filepath"]):
        last_good_file = last_track["filepath"].encode("utf-8")
    elif last_good_file:
        log_warning("Replaying last good file due to an error.")

    return last_good_file


def ices_get_metadata():
    """
    This function, if defined, returns the string you'd like used
    as metadata (ie for title streaming) for the current song. You may
    return null to indicate that the file comment should be used.
    """
    global last_track
    if last_track:
        if "artist" in last_track and "title" in last_track:
            return ("\"%s\" by %s" % (last_track["title"], last_track["artist"])).encode("utf-8")
        return os.path.basename(last_track["filepath"])
    return "Unknown track"


def ices_get_lineno():
    """
    Function used to put the current line number of
    the playlist in the cue file. If you don't care about this number
    don't use it.
    """
    global songnumber
    songnumber = songnumber + 1
    return songnumber


def get_pid_path():
    return get_user_path("ices0.pid")


def cmd_config(arg=None, *args):
    if arg == "help":
        print "Opens the config file in your text editor."
        exit(1)

    elif arg is not None:
        print "This command takes no argument."
        exit(1)

    edit_file(get_config("ices0.xml", DEFAULT_CONFIG))


def cmd_run(arg=None, *args):
    if arg == "help":
        print "Runs ices0 with an ardj-specific config file."
        print "The config file is created if necessary."
        print "You will see the file name and be able to edit it."
        exit(1)

    elif arg is not None:
        print "This command takes no argument."
        exit(1)

    exe = get_exec_path("ices0")
    if not exe:
        print "Could not find ices0 executable in PATH.  Please install."
        osname = os.uname()[3]
        if "Ubuntu" in osname:
            print "Download from <https://bitbucket.org/umonkey/ices0> and compile."
        exit(1)

    config = get_config("ices0.xml", DEFAULT_CONFIG)
    print "Running %s with config file %s -- edit if necessary, then restart." % (exe, config)

    run3([exe, "-c", config])


def skip():
    send_signal(get_pid_path(), 10)  # USR1


def reload():
    send_signal(get_pid_path(), 1)  # HUP
