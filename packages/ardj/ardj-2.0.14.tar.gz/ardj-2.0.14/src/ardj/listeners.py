# vim: set fileencoding=utf-8:

import json
import csv
import os
import re
import sys
import time

import ardj.util
from ardj.database import connect
from ardj.log import *
from ardj.webclient import fetch_url
from ardj import config


def get_count():
    """Returns the number of active listeners."""
    url = config.get("icecast_status_url", "http://127.0.0.1:8000/status-json.xsl")

    # expicitly disabled
    if url == "no":
        return

    if not url:
        log_debug('Unable to count listeners: icecast_stats_url not set.')
        return 0

    try:
        data = fetch_url(url, quiet=True)
        parsed = json.loads(data)
        if "icestats" in parsed:
            if "source" in parsed["icestats"]:
                return parsed["icestats"]["source"]["listeners"]
    except Exception, e:
        log_error("could not count listeners: {}: {}", e.__class__.__name__, str(e))

    return 0


def format_data(sql, params, converters, header=None):
    f = csv.writer(sys.stdout)
    if header:
        f.writerow(header)

    rows = connect().fetch(sql, params)
    for row in rows:
        row = [converters[x](row[x]) for x in range(len(row))]
        f.writerow(row)


def get_yesterday_ts():
    """Returns timestamps for yesterday and today midights, according to local
    time zone."""
    now = int(time.time())
    diff = time.daylight and time.altzone or time.timezone
    today = now - (now % 86400) + diff
    if diff < 0:
        today += 86400
    yesterday = today - 86400
    return yesterday, today


def cmd_now():
    """Print current listener count."""
    print get_count()


def cli_total():
    """Prints overall statistics."""
    sql = 'SELECT max(l.ts), t.artist, t.title, SUM(l.listeners) AS count, t.id, t.weight FROM tracks t INNER JOIN playlog l ON l.track_id = t.id WHERE weight > 0 GROUP BY t.artist, t.title ORDER BY artist COLLATE utf8_unicode_ci, title COLLATE utf8_unicode_ci'
    params = []
    format_data(sql, params, [
        lambda d: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(d)),
        lambda x: unicode(x).encode('utf-8'),
        lambda x: unicode(x).encode('utf-8'),
        str,
        str,
        lambda w: '%.02f' % w,
    ], ['last_played', 'artist', 'title', 'listeners', 'track_id', 'weight'])


def cli_yesterday():
    """Prints yesterday's statistics."""
    sql = 'SELECT l.ts, t.id, t.artist, t.title, l.listeners FROM tracks t INNER JOIN playlog l ON l.track_id = t.id WHERE l.ts BETWEEN ? AND ? AND weight > 0 ORDER BY l.ts'
    params = get_yesterday_ts()
    format_data(sql, params, [
        lambda d: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(d)),
        str,
        lambda x: unicode(x).encode('utf-8'),
        lambda x: unicode(x).encode('utf-8'),
        str,
    ], ['time', 'track_id', 'artist', 'title', 'listeners'])
