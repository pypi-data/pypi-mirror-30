#!/usr/bin/env python
# encoding=utf-8

"""ARDJ, an artificial DJ.

This software lets you automate an internet radio station.  Its purpose is to
maintain a database of audio files with metadata, feed ezstream with random
those files based on playlists, let listeners vote for music using an XMPP
client.

To interact with the software you use the `ardj' binary, which simply imports
the `ardj.cli' module and calls the run() method.  Look there to understand how
things work.
"""

import os
import sys


__all__ = ["get_data_path"]

DATA_ROOT = os.path.dirname(os.path.abspath(__file__))


def get_data_path(path):
    return os.path.join(DATA_ROOT, "data", path)


def is_verbose():
    return "-v" in sys.argv


def is_dry_run():
    return "-n" in sys.argv


def get_sample_music():
    """Returns files to pre-seed the media database with."""
    return [get_data_path("cubic_undead.mp3"),
            get_data_path("successful_install.ogg"),
            get_data_path("stefano_mocini_leaving_you_failure_edit.ogg")]
