# encoding=utf-8
#
# replaygain scanner for ardj.
#
# ardj is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# ardj is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
ReplayGain scanner for ardj.

Updates RG info in MP3 and OGG/Vorbis files. Reads track peak/gain from
tags, calculates if none (MP3, OGG and FLAC files only). For MP3 files
the ID3v2 (both TXXX and RVA2) and APEv2 tags are read and written.

Usage:

    from ardj.replaygain import rg_update
    rg_update(filename)

Command line usage:

    ardj replaygain
"""

import os

import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import RVA2, TXXX
from mutagen.apev2 import APEv2

import ardj.util
from ardj.log import *
from ardj.util import utf, run_grab


__all__ = ["rg_update"]


def rg_update(filename):
    """Updates RG if necessary."""
    if rg_check(filename):
        log_debug("replaygain: file {} is ok", filename)
        return True

    peak, gain = read(filename)
    if peak is not None and gain is not None:
        log_debug("replaygain: updating {}", filename)
        return rg_write(filename, peak, gain)

    log_warning('No replaygain for {}: peak={} gain={}', utf(filename), peak, gain)
    return False


def rg_check(filename):
    """Returns True if the file has all ReplayGain data."""
    try:
        tags = mutagen.File(filename)

        if type(tags) != MP3:
            return 'replaygain_track_peak' in tags and 'replaygain_track_gain' in tags
        if 'TXXX:replaygain_track_peak' not in tags or 'TXXX:replaygain_track_gain' not in tags:
            return False
        if 'RVA2:track' not in tags:
            return False
        tags = APEv2(filename)
        return 'replaygain_track_peak' in tags and 'replaygain_track_gain' in tags

    except:
        return False


def read(filename, update=True):
    """Returns (peak, gain) for a file."""
    peak = gain = None

    def parse_rg(tags):
        p = g = None
        if 'replaygain_track_peak' in tags:
            p = float(tags['replaygain_track_peak'][0])
        if 'replaygain_track_gain' in tags:
            value = tags['replaygain_track_gain'][0]
            if value.endswith(' dB'):
                g = float(value[:-3])
            else:
                log_warning('Malformed track gain info: "{}" in {}', value, filename)
        return (p, g)

    try:
        peak, gain = parse_rg(mutagen.File(filename, easy=True))
    except:
        pass

    # Prefer the first value because RVA2 is more precise than
    # APE, formatted as %.2f.
    if peak is None or gain is None:
        try:
            peak, gain = parse_rg(APEv2(filename))
        except:
            pass

    if (peak is None or gain is None) and update:
        scanner = None
        ext = os.path.splitext(filename)[1].lower()
        if ext in ('.mp3'):
            scanner = ['nice', '+15', 'mp3gain', '-q', '-s', 'i', str(filename)]
        elif ext in ('.ogg', '.oga'):
            scanner = ['nice', '+15', 'vorbisgain', '-q', '-f', str(filename)]
        elif ext in ('.flac'):
            scanner = ['nice', '+15', 'metaflac', '--add-replay-gain', str(filename)]

        if not scanner:
            log_warning("Don't know how to calculate ReplayGain for {}", utf(filename))
            return (None, None)

        status, out, err = run_grab(scanner)
        if status == 0:
            peak, gain = read(str(filename), update=False)
        else:
            raise Exception("ReplayGain scanner failed: %s" % out)

    return (peak, gain)


def rg_write(filename, peak, gain):
    """Writes RG tags to file."""
    if peak is None:
        raise Exception('peak is None')
    elif gain is None:
        raise Exception('gain is None')
    try:
        tags = mutagen.File(filename)
        if type(tags) == MP3:
            tags['TXXX:replaygain_track_peak'] = TXXX(encoding=0, desc=u'replaygain_track_peak', text=[u'%.6f' % peak])
            tags['TXXX:replaygain_track_gain'] = TXXX(encoding=0, desc=u'replaygain_track_gain', text=[u'%.2f dB' % gain])
            tags['RVA2:track'] = RVA2(desc=u'track', channel=1, peak=peak, gain=gain)
            tags.save()

            # Additionally write APEv2 tags to MP3 files.
            try:
                tags = APEv2(filename)
            except:
                tags = APEv2()
            tags['replaygain_track_peak'] = '%.6f' % peak
            tags['replaygain_track_gain'] = '%.2f dB' % gain
            tags.save(filename)
        else:
            tags['replaygain_track_peak'] = '%.6f' % peak
            tags['replaygain_track_gain'] = '%.2f dB' % gain
            tags.save(filename)
        return True
    except:
        pass
    return False


def cmd_scan(arg=None, *args):
    if arg == "help":
        print "Adds replaygain tags to all your mp3, ogg and flac files that don't have it."
        exit(1)

    elif arg is not None:
        print "This command takes no argument."
        exit(1)

    for root, folders, files in os.walk(get_user_path("music")):
        for fn in files:
            update(fn)
