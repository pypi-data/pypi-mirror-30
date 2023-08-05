# encoding=utf-8

"""
Basic playlist functions.

Reads the playlists from file, caches, reloads when needed.

Does NOT hold any logic.
"""

import os
import yaml

from ardj.log import *
from ardj.util import get_user_path


DEFAULT_CONFIG = """# Play a jingle every 15 minutes.
- name: jingles
  labels: [jingle]
  delay: 15

# Heavy rotation
- name: default_heavy
  labels: [music, +promote]
  delay: 20

# Unless other rules apply, play everything with the "music" label.
- name: music
  labels: [music]
"""


class Loader(object):
    instance = None

    def __init__(self, path):
        self.path = path
        self.data = {}
        self.mtime = 0

    @classmethod
    def load(cls):
        if cls.instance is None:
            cls.instance = cls(get_user_path("playlist.yaml"))
        cls.instance.refresh()
        return cls.instance

    def refresh(self):
        if not os.path.exists(self.path):
            log_debug("config: file {} does not exist, using defaults", self.path)
            self.data = yaml.load(DEFAULT_CONFIG)

        else:
            mtime = os.stat(self.path).st_mtime
            if mtime > self.mtime:
                with open(self.path, "rb") as f:
                    if self.mtime:
                        log_debug("playlist: reloading from {}", self.path)
                    self.data = yaml.load(f.read())
                self.mtime = mtime

        return self

    @classmethod
    def get(cls):
        instance = cls.load()
        return instance.data


def get_playlists():
    return Loader.get()


def get_playlist_path():
    return get_user_path("playlist.yaml")
