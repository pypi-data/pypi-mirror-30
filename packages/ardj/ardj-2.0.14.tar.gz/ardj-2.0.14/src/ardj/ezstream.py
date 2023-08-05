# encoding=utf-8

"""
Ezstream gateway for ardj.

Runs ezstream with a config file tweaked for ardj.
"""

import os

from ardj.util import get_user_path, get_exec_path, edit_file, get_config, run2, send_signal


DEFAULT_CONFIG = """<!--
This is the configuration file for ezstream, your playlist server.
It is tweaked to work with ardj, the artificial DJ complex.
You can quickly access this file with the `ardj ezstream-config' command.

By default this config file makes ezstream send music to this access point:

  http://127.0.0.1:8000/music.mp3

Normally you would use a public DNS name instead of 127.0.0.1, but the port
number will remain in the url.

--><ezstream>
    <url>http://localhost:8000/music.mp3</url>
    <sourcepassword>ardj_source</sourcepassword>
    <format>MP3</format>
    <playlist_program>1</playlist_program>
    <filename>{BIN}/ardj-next</filename>

    <metadata_progname>{BIN}/ardj-ezmeta</metadata_progname>
    <metadata_format>"@t@" by @a@</metadata_format>

    <svrinfoname>ARDJ based radio</svrinfoname>
    <svrinfourl>http://umonkey.net/ardj/</svrinfourl>
    <svrinfogenre>Music</svrinfogenre>
    <svrinfodescription>This radio is powered by ardj.</svrinfodescription>
    <svrinfobitrate>128</svrinfobitrate>
    <svrinfochannels>2</svrinfochannels>
    <svrinfosamplerate>44100</svrinfosamplerate>
    <svrinfopublic>1</svrinfopublic>

    <reencode>
        <enable>1</enable>
        <encdec>
            <format>FLAC</format>
            <match>.flac</match>
            <decode>flac -s -d --force-raw-format --sign=signed --endian=little -o - "@T@"</decode>
        </encdec>
        <encdec>
            <format>MP3</format>
            <match>.mp3</match>
            <decode>mpg123 --rva-radio --stereo --rate 44100 --stdout "@T@"</decode>
            <encode>lame --preset cbr 128 -r -s 44.1 --bitwidth 16 - -</encode>
        </encdec>
        <encdec>
            <format>VORBIS</format>
            <match>.ogg</match>
            <decode>sox --replay-gain track "@T@" -r 44100 -c 2 -t raw -e signed-integer -</decode>
            <encode>oggenc -r -B 16 -C 2 -R 44100 --raw-endianness 0 -q 1.5 -t "@M@" -</encode>
        </encdec>
    </reencode>
</ezstream>
"""


def check_file_perms():
    # For some fucking reason ezstream hates group writable files.
    # Try to fix it.
    for exe in ("ardj-next", "ardj-ezmeta"):
        path = get_exec_path(exe)
        if path and os.access(path, os.W_OK):
            try:
                os.chmod(path, 0755)
            except OSError:
                pass  # ezstream will issue its own error message


def get_pid_path():
    return get_user_path("ezstream.pid")


def cmd_config(arg=None, *args):
    if arg == "help":
        print "Opens the config file in your text editor."
        exit(1)

    elif arg is not None:
        print "This command takes no argument."
        exit(1)

    edit_file(get_config("ezstream.xml", DEFAULT_CONFIG))


def cmd_run(arg=None, *args):
    if arg == "help":
        print "Runs ezstream with ardj-specific config file."
        print "The config file is created if necessary."
        print "You will see the file name and be able to edit it."
        exit(1)

    elif arg is not None:
        print "This command takes no argument."
        exit(1)

    exe = get_exec_path("ezstream")
    if not exe:
        print "Could not find ezstream executable in PATH.  Please install."
        osname = os.uname()[3]
        if "Ubuntu" in osname:
            print "Example: sudo apt-get install ezstream"
        exit(1)

    check_file_perms()

    if not get_exec_path("mpg123"):
        print "*** WARNING: install mpg123 to read mp3 files."
    if not get_exec_path("sox"):
        print "*** WARNING: install sox to read Ogg/Vorbis files."
    if not get_exec_path("flac"):
        print "*** WARNING: install flac to read FLAC files."
    if not get_exec_path("lame"):
        print "*** WARNING: install lame to publish MP3 streams."
    if not get_exec_path("oggenc"):
        print "*** WARNING: install oggenc to publish Ogg/Vorbis streams."

    config = get_config("ezstream.xml", DEFAULT_CONFIG)
    print "Running %s with config file %s -- edit if necessary, then restart." % (exe, config)

    ret = run2([exe, "-c", config], get_pid_path())
    if ret != 0:
        exit(1)


def is_running():
    fn = get_pid_path()
    return os.path.exists(fn)


def skip():
    send_signal(get_pid_path(), 10)
