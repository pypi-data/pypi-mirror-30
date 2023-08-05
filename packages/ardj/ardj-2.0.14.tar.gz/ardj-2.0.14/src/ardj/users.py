# encoding=utf-8

import time

from ardj import config
from ardj.database import connect
from ardj.models import Vote


def get_voters():
    """Returns information on voters in tuples (email, count, weight)."""
    db = connect()
    rows = db.fetch('SELECT v.email, COUNT(*) AS c, k.weight '
        'FROM votes v LEFT JOIN karma k ON k.email = v.email '
        'GROUP BY v.email ORDER BY c DESC, k.weight DESC, v.email')
    return rows


def get_top_recent_voters(count=10, days=14):
    """Returns top 10 voters for last 2 weeks."""
    if not count:
        return []
    delta = int(time.time()) - days * 86400

    db = connect()

    emails = []
    for row in db.fetch("SELECT `email`, COUNT(*) AS `c` FROM `votes` WHERE `ts` >= ? GROUP BY `email` ORDER BY `c` DESC LIMIT %u" % count, [delta]):
        emails.append(row[0])

    return emails


def get_admins(safe=False):
    """Returns jids/emails of admins."""
    admins = config.get("jabber_admins", [])
    if not safe:
        count = config.get("promote_voters", 0)
        days = config.get("promote_voters_days", 14)
        admins += get_top_recent_voters(count, days)
    return admins


def get_aliases():
    """Returns user aliases."""
    return config.get("jabber_aliases", {})


def resolve_alias(jid):
    """Resolves an addres according to configured aliases."""
    for main, other in get_aliases().items():
        if jid in other:
            return main
    return jid


def cmd_vote_stats(*args):
    """Show vote statistics"""
    daily = {}
    hourly = {}

    for vote in Vote.find_all():
        ts = time.gmtime(vote["ts"])

        if prefix is not None:
            if not time.strftime("%Y-%m-%d %H:%M:%S", ts).startswith(prefix):
                continue

        day = int(time.strftime("%w", ts)) or 7
        daily[day] = daily.get(day, 0) + 1

        hour = int(time.strftime("%H", ts))
        hourly[hour] = hourly.get(hour, 0) + 1

    def dump_votes(votes, prefix):
        total = float(sum(votes.values()))
        for k, v in votes.items():
            print "%s,%u,%u" % (prefix, k, int(v))

    dump_votes(daily, "D")
    dump_votes(hourly, "H")
