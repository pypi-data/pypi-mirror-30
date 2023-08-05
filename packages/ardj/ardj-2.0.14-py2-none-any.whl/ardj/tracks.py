# encoding=utf-8

"""Track management for ardj.

Contains functions that interact with the database in order to modify or query
tracks.
"""

import json
import os
import random
import re
import subprocess
import sys
import time
import traceback
import urllib

from ardj.chat import chat_say

import ardj.listeners
import ardj.scrobbler
import ardj.tags

from ardj import config
from ardj import is_dry_run, is_verbose
from ardj.database import connect, transaction
from ardj.log import *
from ardj.models import Track as Track2
from ardj.playlist import get_playlists
from ardj.users import resolve_alias
from ardj.util import utf, deutf, lower
from ardj.worker import add_task


KARMA_TTL = 30.0
STICKY_LABEL_FILE_NAME = "~/.ardj/sticky.json"


def log_playlist(message, *args, **kwargs):
    if config.get("debug_playlist") == "yes":
        log_debug("playlist: " + message, *args, **kwargs)


def expand(lst):
    """Expands ranges specified in the list.  For example, this:

    ["1", "3-5", "7"]

    Is expanded to:

    ["1", "3", "4", "5", "7"]

    This function is usually actively used in the playlists.
    """
    result = []
    for item in lst:
        if '-' in str(item):
            bounds = item.split('-')
            result += range(int(bounds[0]), int(bounds[1]))
        else:
            result.append(item)
    return result


class Forbidden(Exception):
    pass


class SamplePlaylist(object):
    """
    Default playlist handler.

    Used when the database is empty.
    """
    FILENAME = "~/.ardj-fallback-playlist.txt"

    def pick_file(self):
        playlist = self.load_playlist()
        if not playlist:
            return None

        playlist.append(playlist.pop(0))  # shift
        self.save_playlist(playlist)

        return playlist[0]

    def save_playlist(self, playlist):
        with open(os.path.expanduser(self.FILENAME), "wb") as f:
            f.write("\n".join(playlist))

    def load_playlist(self):
        playlist = self.load_saved_playlist()
        playlist = self.add_default_tracks(playlist)
        playlist = self.remove_missing_files(playlist)
        return playlist

    def load_saved_playlist(self):
        fn = os.path.expanduser(self.FILENAME)
        if not os.path.exists(fn):
            return []

        with open(fn, "rb") as f:
            raw_names = f.read().strip().splitlines()
            return filter(os.path.exists, raw_names)

    def add_default_tracks(self, playlist):
        from ardj import get_sample_music

        for fn in get_sample_music():
            fp = os.path.abspath(fn)
            if fp not in playlist:
                playlist.append(fp)

        return playlist

    def remove_missing_files(self, playlist):
        return filter(os.path.exists, playlist)


class Playlist(dict):
    def add_ts(self, stats):
        self['last_played'] = 0
        if self['name'] in stats:
            self['last_played'] = stats[self['name']]
        return self

    def match_track(self, track):
        if not isinstance(track, dict):
            raise TypeError
        if not self.match_labels(track.get('labels')):
            return False
        if not self.match_repeat(track.get('count', 0)):
            return False
        if not self.match_weight(track.get('weight', 1.0)):
            return False
        return True

    def match_weight(self, other):
        if '-' not in self.get('weight', ''):
            return True
        min, max = [float(x) for x in self.get('weight').split('-', 1)]
        if other >= min and other <= max:
            return True
        return False

    def match_repeat(self, other):
        if 'repeat' not in self or not other:
            return True
        return other < self['repeat']

    def match_labels(self, other):
        """Checks whether labels apply to this playlist."""
        if not other:
            return False

        plabels = self.get('labels', [self.get('name')])
        success = False

        for plabel in plabels:
            if plabel.startswith('-'):
                if plabel[1:] in other:
                    return False
            if plabel.startswith('+'):
                if plabel[1:] not in other:
                    return False
            elif plabel in other:
                success = True

        return success

    def is_active(self, timestamp=None):
        """Checks whether the playlist can be used right now."""
        now = time.localtime(timestamp)

        now_ts = time.mktime(now)
        now_day = int(time.strftime('%w', now))
        now_hour = int(time.strftime('%H', now))
        now_minutes = int(time.strftime('%M', now))

        if 'delay' in self and self['delay'] * 60 + self['last_played'] >= now_ts:
            return False
        if 'hours' in self and now_hour not in self.get_hours():
            return False
        if 'days' in self and now_day not in self.get_days():
            return False
        if 'minutes' in self and now_minutes not in self.get_minutes():
            return False
        return True

    def get_days(self):
        return expand(self['days'])

    def get_hours(self):
        return expand(self['hours'])

    def get_minutes(self):
        return expand(self['minutes'])

    @classmethod
    def get_active(cls, timestamp=None):
        return [p for p in cls.get_all() if p.is_active(timestamp)]

    @classmethod
    def get_all(cls):
        """Returns information about all known playlists.  Information from
        playlist.yaml is complemented by the last_played column of the
        `playlists' table."""
        db = connect()
        stats = dict(db.fetch('SELECT name, last_played FROM playlists WHERE name IS NOT NULL AND last_played IS NOT NULL'))
        return [cls(p).add_ts(stats) for p in get_playlists()]

    @classmethod
    def touch_by_track(cls, track_id):
        """Finds playlists that contain this track and updates their last_played
        property, so that they could be delayed properly."""
        track = get_track_by_id(track_id)
        ts = int(time.time())

        db = connect()

        for playlist in cls.get_all():
            name = playlist.get('name')
            if name and playlist.match_track(track):
                log_playlist('track {} touches playlist "{}".', track_id, name.encode("utf-8"))
                rowcount = db.execute('UPDATE playlists SET last_played = ? WHERE name = ?', (ts, name, ))
                if rowcount == 0:
                    db.execute('INSERT INTO playlists (name, last_played) VALUES (?, ?)', (name, ts, ))


class Track(dict):
    table_name = "tracks"
    fields = ("id", "owner", "filename", "artist", "title", "length", "weight", "count", "last_played", "real_weight", "image", "download")
    key_name = "id"

    def get_labels(self):
        db = connect()
        if "labels" not in self:
            labels = set()
            for row in db.fetch("SELECT label FROM labels WHERE track_id = ?", [self["id"]]):
                labels.add(row[0])
            self["labels"] = sorted(list(labels))
        return self["labels"]

    def get_artist_url(self):
        if "lastfm:noartist" in self.get_labels():
            return None

        def q(v):
            return urllib.quote(v.encode("utf-8"))

        return "http://www.last.fm/music/%s" % q(self["artist"])

    def get_track_url(self):
        if "lastfm:notfound" in self.get_labels():
            return None

        def q(v):
            return urllib.quote(v.encode("utf-8"))

        return "http://www.last.fm/music/%s/_/%s" % (q(self["artist"]), q(self["title"]))

    @classmethod
    def get_by_id(cls, track_id):
        if not track_id:
            return None

        db = connect()
        for row in db.fetch_dict("SELECT * FROM tracks WHERE id = ?", [track_id]):
            return Track(row)

    @classmethod
    def get_last(cls):
        db = connect()
        for row in db.fetch_dict("SELECT * FROM tracks ORDER BY last_played DESC LIMIT 1"):
            return Track(row)

    def get_last_vote(self, sender):
        db = connect()
        for row in db.fetch("SELECT vote FROM votes WHERE track_id = ? AND email = ? ORDER BY track_id DESC", [self["id"], sender]):
            return row[0]
        return 0

    def get_filepath(self):
        return get_real_track_path(self["filename"])


class Sticky(dict):
    def __init__(self):
        self.fn = os.path.expanduser(STICKY_LABEL_FILE_NAME)
        if os.path.exists(self.fn):
            with open(self.fn, "rb") as f:
                self.update(json.loads(f.read()))

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.flush()

    def flush(self):
        with open(self.fn, "wb") as f:
            f.write(json.dumps(dict(self)))
            log_playlist("wrote {}", self.fn)

    def __getitem__(self, k):
        return self.get(k)


def get_real_track_path(filename):
    return os.path.join(config.get_path("musicdir"), filename)


def get_track_by_id(track_id, sender=None):
    """Returns track description as a dictionary.

    If the track does not exist, returns None.  Extended properties,
    such as labels, are also returned.

    Arguments:
    track_id -- identified the track to return.
    cur -- unused.
    """
    track = Track.get_by_id(track_id)
    if track is None:
        return None

    track["labels"] = track.get_labels()
    if track.get('filename'):
        track['filepath'] = get_real_track_path(track['filename'])

    track["track_url"] = track.get_track_url()
    track["artist_url"] = track.get_artist_url()

    if sender is not None:
        track["bookmark"] = "bm:%s" % sender in track["labels"]
        track["vote"] = track.get_last_vote(sender)
    else:
        track["bookmark"] = False

    track["labels"] = [l for l in track["labels"] if not l.startswith("bm:")]

    return track


def get_last_track_id():
    """Returns id of the last played track.

    If the database is empty, returns None, otherwise an integer.

    Keyword arguments:
    cur -- database cursor, created if None.
    """
    db = connect()
    for row in db.fetch("SELECT id FROM tracks ORDER BY last_played DESC LIMIT 1"):
        return row[0]


def get_last_track():
    """Returns the full description of the last played track.

    Calls get_track_by_id(get_last_track_id()).
    """
    return get_track_by_id(get_last_track_id())


def identify(track_id, unknown='an unknown track'):
    track = get_track_by_id(track_id)
    if not track:
        return unknown
    return u'«%s» by %s [%u]' % (track.get('title', 'untitled'), track.get('artist', 'unknown artist'), track_id)


def queue(track_id, owner=None):
    """Adds the track to queue."""
    db = connect()
    res = db.execute('INSERT INTO queue (track_id, owner) VALUES (?, ?)', (track_id, (owner or 'ardj').lower(), ))
    return res


def get_queue():
    rows = connect().fetch("SELECT track_id FROM queue ORDER BY id")
    return [get_track_by_id(row[0]) for row in rows]


def find_ids(pattern, sender=None, limit=None):
    search_order = 'weight DESC'
    search_args = []
    search_labels = []
    search_ids = []

    args = [a for a in pattern.split(' ') if a.strip()]
    for arg in args:
        if arg == '-r':
            search_order = 'RANDOM()'
        elif arg == '-l':
            search_order = 'id DESC'
        elif arg == '-f':
            search_order = 'id'
        elif arg == '-c':
            search_order = 'count DESC'
        elif arg == '-c-':
            search_order = 'count ASC'
        elif arg == '-b' and sender is not None:
            search_labels.append('bm:' + sender.lower())
            search_ids = None
        elif arg.isdigit():
            if search_ids is not None:
                search_ids.append(arg)
        elif arg.startswith('#'):
            search_labels.append(arg[1:])
            search_ids = None
        else:
            search_args.append(arg)
            search_ids = None

    if search_ids:
        return [int(x) for x in search_ids]

    pattern = u' '.join(search_args)

    params = []
    where = []

    if search_labels:
        _add_label_filter(search_labels, where, params)

    if search_args:
        like = u' '.join(search_args)
        where.append('(ULIKE(artist, ?) OR ULIKE(title, ?))')
        params.append(like)
        params.append(like)

    if not params:
        return []

    sql = 'SELECT id FROM tracks WHERE weight > 0 AND %s ORDER BY %s' % (' AND '.join(where), search_order)
    if limit is not None:
        sql += ' LIMIT %u' % limit
    rows = connect().fetch(sql, params)
    return [row[0] for row in rows]


def _add_label_filter(labels, where, params):
    """Adds condition for filtering tracks by labels."""
    other_labels = []

    for label in labels:
        if label.startswith("+"):
            where.append('id IN (SELECT track_id FROM labels WHERE label = ?)')
            params.append(label[1:])
        elif label.startswith("-"):
            where.append('id NOT IN (SELECT track_id FROM labels WHERE label = ?)')
            params.append(label[1:])
        else:
            other_labels.append(label)

    if other_labels:
        sql = "id IN (SELECT track_id FROM labels WHERE label IN (%s))" % ", ".join(['?'] * len(other_labels))
        where.append(sql)
        params.extend(other_labels)


def add_labels(track_id, labels, owner=None):
    db = connect()

    if labels:
        for label in labels:
            if label.startswith('-'):
                db.execute('DELETE FROM labels WHERE track_id = ? AND label = ?', (track_id, label.lstrip('-'), ))
            elif db.fetch('SELECT 1 FROM labels WHERE track_id = ? AND label = ?', (track_id, label.lstrip('+'), )):
                pass
            else:
                db.execute('INSERT INTO labels (track_id, label, email) VALUES (?, ?, ?)', (track_id, label.lstrip('+'), owner or 'ardj', ))

    add_task("tags.write:%u" % int(track_id))

    res = track.get_labels()
    return res


def update_track(properties):
    """Updates valid track attributes.

    Loads the track specified in properties['id'], then updates its known
    fields with the rest of the properties dictionary, then saves the
    track.  If there's the "labels" key in properties (must be a list),
    labels are added (old are preserved) to the `labels` table.

    If there's not fields to update, a message is written to the debug log.
    """
    if not isinstance(properties, dict):
        raise Exception('Track properties must be passed as a dictionary.')
    if 'id' not in properties:
        raise Exception('Track properties have no id.')

    db = connect()

    sql = []
    params = []
    for k in properties:
        if k in ('filename', 'artist', 'title', 'length', 'weight', 'count', 'last_played', 'owner', 'real_weight', 'download', 'image'):
            sql.append(k + ' = ?')
            params.append(properties[k])

    if not sql:
        log_debug('No fields to update.')
    else:
        params.append(properties['id'])
        sql = 'UPDATE tracks SET ' + ', '.join(sql) + ' WHERE id = ?'
        db.execute(sql, tuple(params))

    if properties.get('labels'):
        add_labels(properties['id'], properties['labels'], owner=properties.get('owner'))

    add_task("tags.write:%u" % int(properties["id"]))


@transaction
def cmd_purge(*args):
    """
    Deletes tracks with zero weight.

    Removes files, track entries are left in the database to prevent reloading.
    """

    db = connect()

    music_dir = config.get_path("musicdir")
    for track_id, filename in db.fetch('SELECT id, filename FROM tracks WHERE weight > 0 AND filename IS NOT NULL'):
        abs_filename = os.path.join(music_dir, filename)
        if not os.path.exists(abs_filename):
            log_warning('Track {} vanished ({}), deleting.', track_id, filename)
            db.execute('UPDATE tracks SET weight = 0 WHERE id = ?', (track_id, ))

    db.execute('DELETE FROM queue WHERE track_id NOT IN (SELECT id FROM tracks)')
    db.execute('DELETE FROM labels WHERE track_id NOT IN (SELECT id FROM tracks)')
    db.execute('DELETE FROM votes WHERE track_id NOT IN (SELECT id FROM tracks)')

    db.purge()  # vacuum etc


def get_urgent():
    """Returns current playlist preferences."""
    db = connect()
    for row in db.fetch('SELECT labels FROM urgent_playlists WHERE expires > ? ORDER BY expires', [int(time.time())]):
        return re.split('[,\s]+', row[0])


def extract_duration(play_args):
    duration = 60

    new_args = []
    for arg in re.split("\s+", play_args):
        if arg.startswith("--time="):
            duration = int(arg[7:])
        else:
            new_args.append(arg)
    return duration, u" ".join(new_args)


def set_urgent(args):
    """Sets the music filter.

    Sets music filter to be used for picking random tracks.  If set, only
    matching tracks will be played, regardless of playlist.yaml.  Labels
    must be specified as a string, using spaces or commas as separators.
    Use "all" to reset.
    """
    db = connect()
    db.execute('DELETE FROM urgent_playlists')

    if args == 'all':
        chat_say(u"Returning to normal playlists.")
    else:
        duration, args = extract_duration(args)
        expires = time.time() + duration * 60
        db.execute('INSERT INTO urgent_playlists (labels, expires) VALUES (?, ?)', (args, int(expires), ))
        chat_say(u"Playlist for next %u minutes: %s." % (duration, args))


def add_vote(track_id, email, vote, update_karma=False):
    """Adds a vote for/against a track.

    The process is: 1) add a record to the votes table, 2) update email's
    record in the karma table, 3) update weight for all tracks email voted
    for/against.

    Votes other than +1 and -1 are skipped.

    Returns track's current weight.
    """
    email = email.lower()

    log_debug("vote: recording {} from {} for track {}", vote, email, track_id)

    if not config.get("enable_voting", True):
        raise Forbidden("Voting disabled by the admins.")

    # Normalize the vote.
    if vote > 0:
        vote = 1
    elif vote < 0:
        vote = -1

    # Resolve aliases.
    email = resolve_alias(email)

    db = connect()

    last_played = current_weight = None
    for row in db.fetch("SELECT last_played, weight FROM tracks WHERE id = ?", [track_id]):
        last_played, current_weight = row

    if last_played is None and current_weight is None:
        return  # empty database
    elif not last_played:
        raise RuntimeError('This track was never played.')
    elif current_weight <= 0:
        raise RuntimeError("Can't vote for deleted tracks.")

    rows = db.fetch("SELECT COUNT(*) FROM votes WHERE track_id = ? "
        "AND email = ? AND vote = ? AND ts >= ?", [track_id, email, vote,
        last_played])
    for row in rows:
        vote_count = row[0]

    db.execute('INSERT INTO votes (track_id, email, vote, ts) '
        'VALUES (?, ?, ?, ?)', (track_id, email, vote, int(time.time()), ))

    # Update current track weight.
    if not vote_count:
        current_weight = max(current_weight + vote * 0.25, 0.01)
        db.execute('UPDATE tracks SET weight = ? WHERE id = ?', (current_weight, track_id, ))

        update_real_track_weight(track_id)

    for row in db.fetch('SELECT weight FROM tracks WHERE id = ?', [track_id]):
        real_weight = row[0]

    return real_weight


def get_vote(track_id, email):
    return get_track_votes(track_id).get(email.lower(), 0)


def get_track_votes(track_id):
    results = {}
    db = connect()
    for email, vote in db.fetch("SELECT email, vote FROM votes WHERE track_id = ?", (track_id, )):
        results[email.lower()] = vote
    return results


def add_file(path, labels=None):
    """Adds the file to the database.

    Returns track id.  ReplayGain calculation is scheduled for background execution.
    """
    if not os.path.exists(path):
        raise ValueError('file %s not found' % filename)

    root = os.path.abspath(os.path.abspath(config.get_path("musicdir")))

    lpath = os.path.abspath(path)
    spath = os.path.relpath(path, root)

    if "../" in spath:
        log_debug("add_file: root={}", root)
        log_debug("add_file: path={}", path)
        log_debug("add_file: lpath={}", lpath)
        log_debug("add_file: spath={}", spath)
        raise RuntimeError("bad relative track path: %s" % spath)

    tags = ardj.tags.get(lpath) or {}
    duration = tags.get('length', 0)
    labels = tags.get('labels', [])

    track = Track2.get_by_path(deutf(spath))
    if not track:
        track = Track2()
        track["filename"] = spath
    if not track.get("weight"):
        track["weight"] = 1

    track["artist"] = tags.get("artist", u"unknown artist")
    track["title"] = tags.get("title", u"untitled")
    track["length"] = duration
    track.put()

    if labels:
        track.set_labels(labels)

    log_info("Track {} added, artist={}, title={}", track["id"], utf(track["artist"]), utf(track["title"]))

    add_task("replaygain:%u" % track["id"])

    return track


def get_track_id_from_queue():
    """Returns a track from the top of the queue.

    If the queue is empty or there's no valid track in it, returns None.
    """
    db = connect()

    for row in db.fetch('SELECT id, track_id FROM queue ORDER BY id LIMIT 1'):
        track = None

        if not row[1]:
            # pause
            db.execute("DELETE FROM queue WHERE id = ?", [row[0]])
            return None

        track = get_track_by_id(row[1])

        db.execute("DELETE FROM queue WHERE id = ?", [row[0]])

        if track is None:
            return None
        if not track.get('filename'):
            return None
        return row[1]


def get_random_track_id_from_playlist(playlist, skip_artists):
    db = connect()

    sql = 'SELECT id, weight, artist, count, last_played FROM tracks WHERE weight > 0 AND artist IS NOT NULL AND filename IS NOT NULL'
    params = []

    labels = list(playlist.get('labels', [playlist.get('name', 'music')]))
    labels.extend(get_sticky_label(playlist))

    sql, params = add_labels_filter(sql, params, labels)

    repeat_count = playlist.get('repeat')
    if repeat_count:
        sql += ' AND count < ?'
        params.append(int(repeat_count))

    if skip_artists:
        skip_count = int(playlist.get("artist_delay", playlist.get("history", "10")))
        skip_artists = skip_artists[:skip_count]
        if skip_artists:
            sql += ' AND artist NOT IN (%s)' % ', '.join(['?'] * len(skip_artists))
            params += skip_artists

    weight = playlist.get('weight', '')
    if '-' in weight:
        parts = weight.split('-', 1)
        sql += ' AND weight >= ? AND weight <= ?'
        params.append(float(parts[0]))
        params.append(float(parts[1]))

    delay = playlist.get('track_delay')
    if delay:
        sql += ' AND (last_played IS NULL OR last_played <= ?)'
        params.append(int(time.time()) - int(delay) * 60)

    track_id = get_random_row(db.fetch(sql, tuple(params)), playlist.get("strategy", "default"))

    if track_id is not None:
        update_sticky_label(track_id, playlist)
        if playlist.get('preroll'):
            track_id = add_preroll(track_id, playlist.get('preroll'))

    return track_id


def update_sticky_label(track_id, playlist):
    """Updates active sticky labels.  If the playlist has no sticky labels,
    they are reset.  If track has none, they are reset.  If track has some, a
    random one is stored."""
    with Sticky() as sticky:
        # Save the new playlist name.  If it changed -- remove previous label.
        pl_name = playlist.get("name", "unnamed")
        if sticky["playlist"] != pl_name:
            if sticky["label"] is not None:
                log_playlist("playlist changed to {}, dropping sticky label \"{}\".", pl_name, sticky["label"])
                sticky["label"] = None

        sticky["playlist"] = playlist.get("name", "unnamed")

        # There is a sticky label already, nothing to do.
        if sticky["label"]:
            log_playlist("using sticky label {}", utf(sticky["label"]))
            return

        # This playlist has no sticky labels, nothing to do.
        if not playlist.get("sticky_labels"):
            log_playlist("sticky: playlist {} has no sticky_labels.", utf(sticky["playlist"]))
            return

        # Find intersecting labels.
        track = Track.get_by_id(track_id)
        if track is None:
            log_playlist("sticky: track {} not found -- no labels to pick from.", track_id)
            return

        # No intersection, nothing to do.
        labels = list(set(track.get_labels()) & set(playlist["sticky_labels"]))
        if not labels:
            log_playlist("sticky: track {} has no labels to stick to playlist {}.", track["id"], utf(sticky["playlist"]))
            return

        # Store the new sticky label.
        sticky["label"] = random.choice(labels)
        log_playlist("new sticky label: {}", utf(sticky["label"]))


def get_sticky_label(playlist):
    """
    Returns sticky labels that apply to this playlist.
    """
    with Sticky() as sticky:
        # Playlist changed, ignore previously used sticky labels.
        if playlist.get("name", "unnamed") != sticky["playlist"]:
            if sticky["label"]:
                log_playlist("sticky: playlist changed to {}, forgetting old label {}.", utf(playlist.get("name")), utf(sticky["label"]))
            return []

        if not sticky["label"]:
            return []

        log_playlist("sticky: forcing label {}", sticky["label"])
        return [u"+" + sticky["label"]]


def add_labels_filter(sql, params, labels):
    either = [l for l in labels if not l.startswith('-') and not l.startswith('+')]
    neither = [l[1:] for l in labels if l.startswith('-')]
    every = [l[1:] for l in labels if l.startswith('+')]

    if either:
        sql += ' AND id IN (SELECT track_id FROM labels WHERE label IN (%s))' % ', '.join(['?'] * len(either))
        params += either

    if neither:
        sql += ' AND id NOT IN (SELECT track_id FROM labels WHERE label IN (%s))' % ', '.join(['?'] * len(neither))
        params += neither

    if every:
        for label in every:
            sql += ' AND id IN (SELECT track_id FROM labels WHERE label = ?)'
            params.append(label)

    return sql, params


def get_random_row(rows, strategy=None):
    rows = list(rows)

    if not rows:
        return None

    if strategy == "fresh":
        rows.sort(key=lambda row: row[3])
        row = random.choice(rows[:5])
        track_id = row[0]

    elif strategy == "oldest":
        rows.sort(key=lambda row: row[4])
        row = rows[0]
        track_id = row[0]

    else:
        track_id = get_random_row_default(rows)

    log_playlist("picked track {} using strategy '{}'.", track_id, utf(strategy))
    return track_id


def get_random_row_default(rows):
    """Picks a random row using the default strategy.

    First divides track weights by the number of tracks that the artist has,
    then picks a random track based on the updated weight.
    """
    ID_COL, WEIGHT_COL, NAME_COL = 0, 1, 2

    artist_counts = {}
    for row in rows:
        name = row[NAME_COL].lower()
        if name not in artist_counts:
            artist_counts[name] = 0
        artist_counts[name] += 1

    probability_sum = 0
    for row in rows:
        name = row[NAME_COL].lower()
        probability_sum += row[WEIGHT_COL] / artist_counts[name]

    rnd = random.random() * probability_sum
    for row in rows:
        name = row[NAME_COL].lower()
        weight = row[WEIGHT_COL] / artist_counts[name]
        if rnd < weight:
            return row[ID_COL]
        rnd -= weight

    if len(rows):
        log_warning('Bad RND logic, returning first track.')
        return rows[0][ID_COL]

    return None


def get_prerolls_for_labels(labels):
    """Returns ids of valid prerolls that have one of the specified labels."""
    sql = "SELECT tracks.id FROM tracks INNER JOIN labels ON labels.track_id = tracks.id WHERE tracks.weight > 0 AND tracks.filename IS NOT NULL AND labels.label IN (%s)" % ', '.join(['?'] * len(labels))
    db = connect()
    return [row[0] for row in db.fetch(sql, labels)]


def get_prerolls_for_track(track_id):
    """Returns prerolls applicable to the specified track."""
    db = connect()

    ids = set()

    # by artist
    for row in db.fetch("SELECT t1.id FROM tracks t1 INNER JOIN tracks t2 ON t2.artist = t1.artist INNER JOIN labels l ON l.track_id = t1.id WHERE l.label = 'preroll' AND t2.id = ? AND t1.weight > 0 AND t1.filename IS NOT NULL", [track_id]):
        ids.add(row[0])

    # by label
    for row in db.fetch("SELECT t.id, t.title FROM tracks t WHERE t.weight > 0 AND t.filename IS NOT NULL AND t.id IN (SELECT track_id FROM labels WHERE label IN (SELECT l.label || '-preroll' FROM tracks t1 INNER JOIN labels l ON l.track_id = t1.id WHERE t1.id = ?))", [track_id]):
        ids.add(row[0])

    return list(ids)


def add_preroll(track_id, labels=None):
    """Adds a preroll for the specified track.

    Finds prerolls by labels and artist title, picks one and returns its id,
    queueing the input track_id.  If `labels' is explicitly specified, only
    tracks with those labels will be used as prerolls.

    Tracks that have a preroll-* never have a preroll.
    """
    # Skip if the track is a preroll.
    log_playlist("looking for prerolls for track {} (labels={})", track_id, labels)

    db = connect()
    for row in db.fetch("SELECT COUNT(*) FROM labels WHERE track_id = ? AND label LIKE 'preroll-%'", [track_id]):
        log_playlist("track {} is a preroll itself.", track_id)
        return track_id

    if labels:
        prerolls = get_prerolls_for_labels(labels)
    else:
        prerolls = get_prerolls_for_track(track_id)

    log_playlist("found {} prerolls.", len(prerolls))

    if track_id in prerolls:
        prerolls.remove(track_id)

    if prerolls:
        queue(track_id)
        track_id = prerolls[random.randrange(len(prerolls))]
        log_debug("playlist: will play track {} (a preroll).", track_id)

    return track_id


def get_built_in_track():
    """
    Returns a built-in track to play.

    Used when the database is empty.  Tracks are read from a special folder and
    played in a loop.  The playlist is stored in a file named
    ~/.ardj-fallback-playlist.txt
    """
    pl = SamplePlaylist()
    return pl.pick_file()


def get_next_track():
    try:
        track_id = get_next_track_id()
        if not track_id:
            log_warning("Could not find a track to play -- empty database?")
            return None

        track = get_track_by_id(track_id)
        if not track:
            log_warning("No info on track {}", track_id)
            return None

        dump_filename = config.get("dump_last_track")
        if dump_filename is not None:
            dump = json.dumps(track)
            file(dump_filename, "wb").write(dump.encode("utf-8"))

        return track
    except Exception, e:
        log_exception("Could not get a track to play: {}", e)
        return None


def get_next_track_id(update_stats=True):
    """
    Picks a track to play.

    The track is chosen from the active playlists. If nothing could be chosen,
    a random track is picked regardless of the playlist (e.g., the track can be
    in no playlist or in an unexisting one).  If that fails too, None is
    returned.

    Normally returns a dictionary with keys that corresponds to the "tracks"
    table fields, e.g.: filename, artist, title, length, weight, count,
    last_played, playlist.  An additional key is filepath, which contains the
    full path name to the picked track, encoded in UTF-8.

    Before the track is returned, its and the playlist's statistics are
    updated.

    Arguments:
    update_stats -- set to False to not update last_played.
    """
    want_preroll = True
    debug = config.get("debug_playlists") == "yes"

    db = connect()

    dupe_count = int(config.get("dupes", 0))
    if dupe_count:
        skip_artists = list(set([row[0] for row in db.fetch('SELECT artist FROM tracks WHERE artist IS NOT NULL AND last_played IS NOT NULL ORDER BY last_played DESC LIMIT ' + str(dupe_count))]))
    else:
        skip_artists = []

    log_playlist("artists to skip: {}.", u', '.join(skip_artists or ['none']))

    track_id = get_track_id_from_queue()
    if track_id:
        want_preroll = False
        log_playlist('picked track {} from the queue.', track_id)

    if not track_id:
        labels = get_urgent()
        if labels:
            track_id = get_random_track_id_from_playlist({'labels': labels}, skip_artists)
            if track_id:
                log_playlist('picked track {} from the urgent playlist.', track_id)

    if not track_id:
        for playlist in Playlist.get_active():
            log_playlist('looking for tracks in playlist "{}"', utf(playlist.get('name', 'unnamed')))
            labels = playlist.get('labels', [playlist.get('name', 'music')])
            track_id = get_random_track_id_from_playlist(playlist, skip_artists)
            if track_id is not None:
                update_program_name(playlist.get("program"))
                s = Sticky()

                msg = 'picked track %u from playlist "%s" using strategy "%s"' % (track_id, playlist.get('name', 'unnamed').encode("utf-8"), playlist.get("strategy", "default"))
                if s["label"]:
                    msg += " and sticky label \"%s\"" % s["label"]
                log_debug("playlist: {}", msg)
                break

    if not track_id:
        log_debug("playlist: falling back to just any random track from the database.")

        rows = list(db.fetch("SELECT id, weight, artist, count, last_played FROM tracks WHERE weight > 0"))
        track_id = get_random_row(rows)

    if track_id:
        if want_preroll:
            track_id = add_preroll(track_id)

        if update_stats:
            db.execute("UPDATE tracks SET count = count + 1, last_played = ? WHERE id = ?", [int(time.time()), track_id])
            Playlist.touch_by_track(track_id)
            log_playback(track_id)

        shift_track_weight(track_id)

    return track_id


def update_program_name(name):
    """Updates the current program name.

    Only works if the playlist has a non-empty "program" property. The value is
    written to a text file specified in the program_name_file config file
    property."""
    if not name:
        return

    filename = config.get("program_name_file")
    if not filename:
        return

    current = None
    if os.path.exists(filename):
        current = file(filename, "rb").read().decode("utf-8").strip()

    if current != name:
        file(filename, "wb").write(name.encode("utf-8"))

        command = config.get_path("program_name_handler")
        if os.path.exists(command):
            log_info("Running {} ({})", utf(command), utf(name))
            subprocess.Popen(command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def shift_track_weight(track_id):
    db = connect()

    for row in db.fetch("SELECT weight, real_weight FROM tracks WHERE id = ?", [track_id]):
        weight, real_weight = row

    old_weight = weight

    if weight < real_weight:
        weight = min(weight + 0.1, real_weight)
    elif weight > real_weight:
        weight = max(weight - 0.1, real_weight)

    db.execute("UPDATE tracks SET weight = ? WHERE id = ?", [weight, track_id])

    log_playlist("weight for track {} changed from {} to {}", track_id, old_weight, weight)


def log_playback(track_id, listener_count=None, ts=None):
    """Logs that the track was played.

    Only logs tracks with more than zero listeners."""
    if listener_count is None:
        listener_count = ardj.listeners.get_count()
    db = connect()
    db.execute('INSERT INTO playlog (ts, track_id, listeners) VALUES (?, ?, ?)', (int(ts or time.time()), int(track_id), listener_count, ))


def update_real_track_weight(track_id):
    """Returns the real track weight, using the last vote for each user."""
    db = connect()

    results = {}
    rows = db.fetch('SELECT v.email, v.vote * k.weight FROM votes v '
        'INNER JOIN karma k ON k.email = v.email '
        'WHERE v.track_id = ? ORDER BY v.ts', (track_id, ))
    for email, vote in rows:
        results[email] = vote

    real_weight = max(sum(results.values()) * 0.25 + 1, 0.01)

    db.execute('UPDATE tracks SET real_weight = ? WHERE id = ?', (real_weight, track_id, ))

    return real_weight


def update_real_track_weights():
    """Updates the real_weight column for all tracks.  To be used when the
    votes table was heavily modified or when corruption is possible."""
    db = connect()

    update_karma()
    for row in db.fetch('SELECT id FROM tracks'):
        update_real_track_weight(row[0])


def update_karma():
    """Updates users karma based on their last voting time."""
    db = connect()
    db.execute('DELETE FROM karma')

    now = int(time.time()) / 86400
    for email, ts in db.fetch('SELECT email, MAX(ts) FROM votes GROUP BY email'):
        diff = now - ts / 86400
        if diff == 0:
            karma = 1
        elif diff > KARMA_TTL:
            karma = 0
        else:
            karma = (KARMA_TTL - float(diff)) / KARMA_TTL
        if karma:
            db.execute('INSERT INTO karma (email, weight) VALUES (?, ?)', (email, karma, ))
            if '-q' not in sys.argv:
                print '%.04f\t%s (%u)' % (karma, email, diff)


def merge(id1, id2):
    """Merges two tracks."""
    id1, id2 = sorted([id1, id2])

    t1 = get_track_by_id(id1)
    t2 = get_track_by_id(id2)

    for k in ('real_weight', 'last_played', 'weight'):
        t1[k] = max(t1[k] or 0, t2[k] or 0)
    if t2["count"]:
        t1['count'] += t2['count']

    t1['labels'] = list(set(t1['labels'] + t2['labels']))

    db = connect()
    db.execute('UPDATE labels SET track_id = ? WHERE track_id = ?', (id1, id2, ))
    db.execute('UPDATE votes SET track_id = ? WHERE track_id = ?', (id1, id2, ))
    db.execute('UPDATE playlog SET track_id = ? WHERE track_id = ?', (id1, id2, ))

    update_track(t1)

    t2['weight'] = 0
    update_track(t2)

    update_real_track_weight(id1)


def update_track_lengths(only_ids=None):
    db = connect()
    rows = db.fetch('SELECT id, filename, length '
        'FROM tracks WHERE weight > 0 AND filename IS NOT NULL')

    updates = []
    for id, filename, length in rows:
        if only_ids is not None and id not in only_ids:
            continue

        filepath = get_real_track_path(filename)
        if not os.path.exists(filepath):
            log_warning("File {} is missing.", utf(filepath))
            continue

        tags = ardj.tags.get(filepath)
        if "length" not in tags:
            log_warning("Length of file {} is unknown.", utf(filepath))
            continue

        if tags["length"] != length:
            print '%u, %s: %s => %s' % (id, filename, length, tags['length'])
            updates.append((tags['length'], id))

    db = connect()
    for length, id in updates:
        db.execute('UPDATE tracks SET length = ? WHERE id = ?', (length, id, ))


def bookmark(track_ids, owner, remove=False):
    """Adds a bookmark label to the specified tracks."""
    db = connect()

    label = 'bm:' + owner.lower()
    for track_id in track_ids:
        db.execute('DELETE FROM labels WHERE track_id = ? AND label = ?', (track_id, label, ))
        if not remove:
            db.execute('INSERT INTO labels (track_id, label, email) VALUES (?, ?, ?)', (track_id, label, owner, ))


def find_by_artist(artist_name):
    db = connect()

    ids = []
    for row in db.fetch('SELECT id FROM tracks WHERE artist = ? COLLATE utf8_unicode_ci', [artist_name]):
        ids.append(row[0])

    return ids


def find_by_filename(pattern):
    db = connect()
    rows = db.fetch('SELECT id FROM tracks WHERE filename LIKE ? COLLATE utf8_unicode_ci', (pattern, ))
    return [row[0] for row in rows]


def find_by_title(title, artist_name=None):
    """Returns track ids by title."""
    db = connect()
    if artist_name is None:
        rows = db.fetch('SELECT id FROM tracks WHERE title = ? COLLATE utf8_unicode_ci', (title, ))
    else:
        rows = db.fetch('SELECT id FROM tracks WHERE title = ? COLLATE utf8_unicode_ci AND artist = ? COLLATE utf8_unicode_ci', (title, artist_name, ))
    return [row[0] for row in rows]


def get_missing_tracks(tracklist, limit=100):
    """Removes duplicate and existing tracks."""
    tmp = {}
    fix = lower

    for track in tracklist:
        artist = fix(track['artist'])
        if artist not in tmp:
            tmp[artist] = {}
        if len(tmp[artist]) >= limit:
            continue
        if find_by_title(track['title'], artist):
            continue
        tmp[artist][fix(track['title'])] = track

    result = []
    for artist in sorted(tmp.keys()):
        for title in sorted(tmp[artist].keys()):
            result.append(tmp[artist][title])

    return result


@transaction
def cmd_mark_long(arg=None, *args):
    if arg == "help":
        print "Marks tracks longer than average with the 'long' label."
        exit(1)

    elif arg is not None:
        print "This command takes no argument."
        exit(1)

    tag = "long"
    length = Track2.get_average_length()

    db = connect()
    db.execute("DELETE FROM `labels` WHERE `label` = ?", (tag, ))
    db.execute("INSERT INTO `labels` (`track_id`, `email`, `label`) SELECT id, \'ardj\', ? FROM tracks WHERE length > ?", (tag, length, ))
    count = db.fetch('SELECT COUNT(*) FROM labels WHERE label = ?', (tag, ))[0][0]

    print "Average length: %s, total long tracks: %u." % (length, count)


def add_label_to_tracks_liked_by(label, jids, sender):
    """Adds the specified to tracks liked by all of the specified jids."""
    if not isinstance(jids, (list, tuple)):
        raise TypeError("jids must be a list or a tuple")

    db = connect()

    _sets = [set(db.fetchcol("SELECT track_id FROM votes WHERE email = ? AND vote > 0", (jid, ))) for jid in jids]
    while len(_sets) > 1:
        _sets[0] &= _sets[1]
        del _sets[1]

    _ids = list(_sets[0])

    db.execute("DELETE FROM labels WHERE label = ?", (label, ))
    for _id in _ids:
        db.execute("INSERT INTO labels (track_id, label, email) VALUES (?, ?, ?)", (_id, label, sender, ))

    return len(_ids)


def add_missing_lastfm_tags():
    db = connect()
    cli = ardj.scrobbler.LastFM()

    skip_labels = set(config.get("scrobbler_skip_labels", []))

    tracks = Track.find_without_lastfm_tags()
    for track in sorted(tracks, key=lambda t: t["id"], reverse=True):
        labels = track.get_labels()

        if skip_labels and set(labels) & skip_labels:
            info = {"tags": ["notfound", "noartist"]}
            print "  implicit notfound, noartist"
        else:
            try:
                info = cli.get_track_info_ex(track["artist"], track["title"])
            except ardj.scrobbler.TrackNotFound:
                # print "  track not found"
                info = {"tags": ["notfound"], "image": None, "download": None}
                if not cli.is_artist(track["artist"]):
                    info["tags"].append("noartist")
                    # print "  artist not found"
            except ardj.scrobbler.BadAuth, e:
                ardj.log.log_error(str(e), e)
                break
            except ardj.scrobbler.Error, e:
                ardj.log.log_error(str(e), e)
                continue
            except Exception, e:
                ardj.log.log_error(str(e), e)
                continue

        lastfm_tags = info["tags"]

        # Add a dummy tag to avoid scanning this track again.  To rescan,
        # delete this tag and scan again periodically.
        if not lastfm_tags:
            lastfm_tags = ["none"]

        print "%6u. %s -- %s" % (track["id"], track["artist"].encode("utf-8"), track["title"].encode("utf-8"))
        print "        %s" % ", ".join(lastfm_tags)

        for tag in lastfm_tags:
            labels.append("lastfm:" + tag.replace(" ", "_"))

        track.set_labels(labels)
        if info.get("image"):
            track.set_image(info["image"])
        if info.get("download"):
            track.set_download(info["download"])

        log_debug("Updated track {} with: {}", track["id"], info)


def dedup_by_filename(verbose=False):
    """Finds tracks that link to the same file and merges them, higher ID to lower."""
    cache = {}

    merge_count = 0

    for track in Track.find_all(deleted=False):
        if not track["weight"]:
            continue

        if track["filename"] in cache:
            if verbose:
                print "Duplicate: %u, %s" % (track["id"], track["filename"])
            merge(cache[track["filename"]], track["id"])
            merge_count += 1
        else:
            cache[track["filename"]] = track["id"]

    return merge_count


def count_available():
    """Returns the number of tracks that are not deleted."""
    for row in connect().fetch("SELECT COUNT(*) FROM tracks WHERE weight > 0"):
        return row[0]


def get_track_to_play_next():
    """
    Describes track to play next

    Queries the database, on failure returns a predefined track.
    """

    import database

    music_dir = config.get_path("musicdir")

    try:
        track = get_next_track()
        if track is not None:
            filepath = os.path.join(music_dir, track["filepath"])
            # track.refresh_tags(filepath)
            track["filepath"] = filepath
            return track
    except Exception, e:
        log_error("ERROR: {}", e)

    count = count_available()
    if not count:
        log_warning("There are NO tracks in the database.  Put some files in {}, then run 'ardj tracks scan'.", utf(music_dir))
    else:
        log_warning("Could not pick a track to play.  Details can be found in the log file.")

    sample = get_built_in_track()
    if sample:
        log_warning("Playing a pre-packaged file.")
        return {"filepath": os.path.realpath(sample)}

    log_error("Could not find sample music.")


def get_artist_names(label=None, weight=0):
    db = connect()
    if label is None:
        rows = db.fetch("SELECT DISTINCT artist FROM tracks WHERE weight > ?", (weight, ))
    else:
        rows = db.fetch("SELECT DISTINCT artist FROM tracks WHERE weight > ? AND id IN (SELECT track_id FROM labels WHERE label = ?)", (weight, label, ))
    return [r[0] for r in rows]


@transaction
def cmd_fix_length():
    """Update track lengths from files (if changed)"""
    ids = [int(n) for n in args if n.isdigit()]
    update_track_lengths(ids)


@transaction
def cmd_shift_weight():
    """Shift current weights to real weights"""
    update_real_track_weights()


@transaction
def cmd_next():
    """Print file name to play next."""
    track = get_track_to_play_next()
    if track:
        log_info("Next track: {}", utf(track["filepath"]))
        print utf(track["filepath"])


@transaction
def cmd_export_csv():
    """Export track info as CSV"""
    from database import Track

    print "id,filename,artist,title,weight,count"
    for track in Track.find_all():
        cells = [track["id"], track["filename"],
            track["artist"] or "Unknown Artist",
            track["title"] or "Untitled",
            track["real_weight"] or "1.0",
            track["count"] or "0"]
        print ",".join([unicode(c).encode("utf-8")
            for c in cells])


@transaction
def cmd_mark_hitlist(arg=None, *args):
    """
    Marks best tracks with the "hitlist" label.

    Only processes tracks labelled with "music".  Before applying the
    label, removes it from the tracks that have it already.
    """

    set_label, check_label = 'hitlist', 'music'

    db = connect()
    db.execute("DELETE FROM labels WHERE label = ?", (set_label, ))

    weight = None
    for row in db.fetch('SELECT real_weight FROM tracks WHERE id IN (SELECT track_id FROM labels WHERE label = ?) ORDER BY real_weight DESC LIMIT 19, 1', [check_label]):
        weight = row[0]

    if weight:
        db.execute('INSERT INTO labels (track_id, label, email) SELECT id, ?, ? FROM tracks WHERE real_weight >= ? AND id IN (SELECT track_id FROM labels WHERE label = ?)', [set_label, 'ardj', weight[0], check_label])


@transaction
def cmd_mark_orphans(*args):
    """
    Labels orphan tracks with "orphan".

    Orphans are tracks that don't belong to a playlist.
    """

    db = connect()

    used_labels = []
    set_label = "orphan"

    for playlist in get_playlists():
        if 'labels' in playlist:
            labels = playlist['labels']
        else:
            labels = [playlist['name']]
        used_labels += [l for l in labels if not l.startswith('-')]
    used_labels = list(set(used_labels))

    if not(used_labels):
        log_warning('Could not mark orphan tracks: no labels are used in playlist.yaml')
        return False

    db.execute('DELETE FROM labels WHERE label = ?', (set_label, ))

    sql = 'SELECT id, artist, title FROM tracks WHERE weight > 0 AND id NOT IN (SELECT track_id FROM labels WHERE label IN (%s)) ORDER BY artist, title' % ', '.join(['?'] * len(used_labels))
    rows = db.fetch(sql, used_labels)
    for row in rows:
        db.execute('INSERT INTO labels (track_id, email, label) VALUES (?, ?, ?)', (int(row[0]), 'ardj', set_label))


@transaction
def cmd_mark_recent(*args):
    """
    Marks last 100 tracks with 'recent'.
    """

    db = connect()

    db.execute('DELETE FROM labels WHERE label = ?', ('recent', ))
    db.execute('INSERT INTO labels (track_id, label, email) SELECT id, ?, ? FROM tracks WHERE id IN (SELECT track_id FROM labels WHERE label = ?) ORDER BY id DESC LIMIT 100', ('recent', 'ardj', 'music', ))

    db.execute('DELETE FROM labels WHERE label = ?', ('fresh', ))
    db.execute('INSERT INTO labels (track_id, label, email) SELECT id, ?, ? FROM tracks WHERE count < 10 AND weight > 0 AND id IN (SELECT track_id FROM labels WHERE label = ?)', ('fresh', 'ardj', 'music', ))

    count = db.execute("SELECT COUNT(*) FROM labels WHERE label = ?", ('fresh', ))
    print 'Found %u fresh songs.' % count


@transaction
def cmd_stats(*args):
    """Show database statistics"""
    count = length = 0
    for track in Track2.where("weight > 0"):
        count += 1
        if track["length"]:
            length += int(track["length"])
    print "%u tracks, %.1f hours." % (count, length / 60 / 60)


@transaction
def cmd_dedup_tracks():
    """Merge duplicate tracks"""
    from tracks import dedup_by_filename
    db = connect()
    count = dedup_by_filename(verbose=True)
    if count:
        print "Removed %u duplicate tracks." % count
    else:
        print "No duplicate tracks found."


def write_tags(track_id):
    track = Track2.get_by_id(track_id)
    if not track:
        log_debug("Track {} not found -- can't save tags.", track_id)
        return False

    path = os.path.join(config.get_path("musicdir"), utf(track["filename"]))
    if not os.path.exists(path):
        log_warning("File {} not found -- can't save tags.", path)
        return False

    tags = ardj.tags.get(path)

    new_tags = {}
    if tags.get("artist") != ["artist"]:
        new_tags["artist"] = track["artist"]
    if tags.get("title") != track["title"]:
        new_tags["title"] = track["title"]

    labels = track.get_labels()
    if tags.get("labels") != labels:
        new_tags["labels"] = labels

    if new_tags:
        log_info("Writing new tags to {}.", path)
        ardj.tags.set(path, new_tags)

    return True


@transaction
def cmd_check_files(*args):
    if args and args[0] == "help":
        print "Scans the music folder for new files."
        print "Removes deleted files from the database."
        exit(1)

    elif args:
        print "This command takes no argument."
        exit(1)

    known = set()

    root = config.get_path("musicdir")

    # Delete missing.
    log_info("Looking for deleted files.")
    for track in Track2.find_all():
        if track["filename"]:
            known.add(track["filename"])

        if track["weight"] == 0:
            continue

        if not track["filename"]:
            log_warning("Track {} has no file -- disabling.", track["id"])
            track["weight"] = 0
            track.put()
            continue

        fn = os.path.join(root, track["filename"])
        if not os.path.exists(fn):
            log_warning("File {} missing -- track {} disabled.", track["filename"], track["id"])
            track["weight"] = 0
            track.put()
            continue

    # Add new.
    log_info("Looking for new files.")
    for folder, unused, files in os.walk(root):
        for fn in files:
            if fn.lower().split(".")[-1] in ("mp3", "ogg", "oga", "flac"):
                lpath = os.path.join(folder, fn)
                spath = os.path.relpath(lpath, root)
                if spath not in known:
                    add_file(lpath)

    log_debug("Finished checking media library.")


@transaction
def cmd_queue_flush(*args):
    Queue.delete_all()
