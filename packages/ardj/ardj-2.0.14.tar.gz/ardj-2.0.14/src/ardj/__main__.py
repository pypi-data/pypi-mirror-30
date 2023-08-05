# encoding=utf-8

"""
Command line interface for ardj
"""

import sys
import traceback


__author__ = "Justin Forest <hex@umonkey.net>"

USAGE = """
Usage: ardj command [args...|help]

Playback control:

  current.json          -- print current track info in JSON
  play                  -- set up urgent playlist for next hour
  queue-flush           -- delete everything from the queue
  reload                -- reload playlists
  skip                  -- skip to next track

Media database control:

  check-files           -- check media library integrity
  db-dedup              -- find and disable duplicate tracks
  db-purge              -- delete stale data
  db-stats              -- show database statistics
  db-vote-stats         -- show vote statistics
  fix-artist-names      -- fix artist names according to last.fm
  lastfm-find-tags      -- add tags to tracks that have none
  mark-hitlist          -- mark best tracks with the 'hitlist' label
  mark-long             -- mark long tracks with the 'long' label
  mark-orphans          -- mark tracks that don't belong to a playlist
  mark-recent           -- mark 100 recently added tracks with the 'recent' label
  replaygain            -- calculate ReplayGain for all tracks
  tags                  -- show tags from specified files
  tracks-export-csv     -- export all track info as CSV
  tracks-fix-length     -- update track length from files (if changed)
  tracks-next           -- show track to play next
  tracks-shift-weight   -- shift current weights to real weights

Database utility:

  db                    -- open database console
  db-init               -- initialize or update database structure
  db-export             -- save all tables to csv files
  db-import             -- read csv files to tables

Icecast commands:

  adrj icecast          -- run the streaming server (see also: ardj loop)
  ardj icecast-config   -- edit the config file

Ezstream commands:

  ardj ezstream         -- run the playlist server (see also: ardj loop)
  ardj ezstream-config  -- edit the config file

Ices0 (ezstream alternative):

  ardj ices             -- run the playlist server (see also: ardj loop)
  ardj ices-config      -- edit the config file

Background processes (usually ran with `ardj loop'):

  ardj icecast          -- runs the streaming server (icecast2)
  ardj ezstream         -- runs the playlist server (ezstream)
  ardj ices             -- runs the other playlist server (ices0)
  ardj scrobbler        -- runs the music scrobbler (last.fm, libre.fm)
  ardj web-server       -- run local web server
  ardj worker           -- perform one background task
  ardj loop subcommand  -- keeps the specified subcommand running forever

Maintenance:

  ardj run              -- run (or attach to) a detached screen with all processes

Other commands:

  config                -- edit config file
  config-get            -- print a configuration file value
  console               -- open command console
  listeners             -- show current listeners counts
  listeners-total       -- export overall statistics to CSV
  listeners-yesterday   -- export yesterday statistics to CSV
  log                   -- follow the log file
  web-add-token         -- create an access token
  web-server            -- run local web server
  web-tokens            -- list valid tokens
"""


def cmd_loop(*args):
    import subprocess
    import time

    if not args:
        print "Please specify a command to repeat, or 'help'."
        exit(1)

    if args[0] == "help":
        print "Usage: ardj loop command [args...]"
        print
        print "Runs the subcommand forever, restarts on failure without manual intervention."
        print "The subcommand is executed as a new process, safe to upgrade on the run."
        print "Restart delay is 5 seconds."
        exit(1)

    if args[0] not in ("icecast", "ezstream", "ices", "scrobbler", "web-server", "worker"):
        print "Subcommand %s not supported." % args[0]
        print "Supported commands are: icecast, ezstream, ices, scrobbler, web-server, worker."
        exit(1)

    command = ["python", "-m", "ardj"] + list(args)

    delay = 5
    if args[0] == "worker":
        delay = 0
        print "Waiting for background tasks."

    while True:
        p = subprocess.Popen(command)
        p.wait()

        if delay or p.returncode != 0:
            print "Will restart in 5 seconds."
            time.sleep(delay)


def main(prog, command=None, *args):
    try:
        if command == "config":
            from ardj.config import cmd_edit
            cmd_edit(*args)

        elif command == "config-get":
            from ardj.config import cmd_get
            cmd_get(*args)

        elif command == "console":
            from ardj.console import run_cli
            run_cli(*args)

        elif command == "db":
            from ardj.database import cmd_console
            cmd_console(*args)

        elif command == "db-dedup":
            from ardj.tracks import cmd_dedup_tracks
            cmd_dedup_tracks(*args)

        elif command == "db-init":
            from ardj.database import cmd_init
            cmd_init(*args)

        elif command == "db-export":
            from ardj import database
            database.cmd_export(*args)

        elif command == "db-import":
            from ardj import database
            database.cmd_import(*args)

        elif command == "db-purge":
            from ardj.database import cmd_purge
            cmd_purge(*args)

        elif command == "db-stats":
            from ardj.tracks import cmd_stats
            cmd_stats(*args)

        elif command == "db-vote-stats":
            from ardj.users import cmd_vote_stats
            cmd_vote_stats(*args)

        elif command == "listeners":
            from ardj.listeners import cmd_now
            cmd_now(*args)

        elif command == "reload":
            from ardj import ices, icecast
            ices.reload()
            icecast.reload()

        elif command == "replaygain":
            from ardj.replaygain import cmd_scan
            cmd_scan(*args)

        elif command == "scrobbler":
            from ardj.scrobbler import cmd_run
            cmd_run(*args)

        elif command == "skip":
            from ardj import ezstream, ices
            ezstream.skip()
            ices.skip()

        elif command == "tracks-fix-length":
            from ardj.tracks import cmd_fix_length
            cmd_fix_length(*args)

        elif command == "tracks-shift-weight":
            from ardj.tracks import cmd_shift_weight
            cmd_shift_weight(*args)

        elif command == "tracks-next":
            from ardj.tracks import cmd_next
            cmd_next(*args)

        elif command == "tracks-export-csv":
            from ardj.tracks import cmd_export_csv
            cmd_export_csv(*args)

        elif command == "web-add-token":
            from ardj.server import cmd_create_token
            cmd_create_token(*args)

        elif command == "web-server":
            from ardj.server import cmd_serve
            cmd_serve(*args)

        elif command == "web-tokens":
            from ardj.server import cmd_tokens
            cmd_tokens(*args)

        elif command == "check-files":
            from ardj import tracks
            tracks.cmd_check_files(*args)

        elif command == "listeners-total":
            from ardj import listeners
            listeners.cli_total(*args)

        elif command == "listeners-yesterday":
            from ardj import listeners
            listeners.cli_yesterday()

        elif command == "tags":
            from ardj import tags
            for fn in args:
                if os.path.exists(fn):
                    print "Tags in %s" % fn
                    for k, v in sorted(tags.get(arg).items(), key=lambda x: x[0]):
                        print '  %s = %s' % (k, v)

        elif command == "current.json":
            from ardj import tracks
            import json
            print json.dumps(tracks.Track.get_last())

        elif command == "queue-flush":
            from ardj import tracks
            tracks.cmd_queue_flush()

        elif command == "fix-artist-names":
            from ardj.scrobbler import LastFM
            from ardj.tracks import get_artist_names
            from ardj.database import connect
            from ardj.models import Track

            cli = LastFM().authorize()
            if cli is None:
                print "Last.fm authentication failed."
                return False

            names = get_artist_names()
            print "Correcting %u artists." % len(names)

            for name in names:
                new_name = cli.get_corrected_name(name)
                if new_name is not None and new_name != name:
                    # logging.info("Correcting artist name \"%s\" to \"%s\"" % (name.encode("utf-8"), new_name.encode("utf-8")))
                    Track.rename_artist(name, new_name)

            connect().commit()

        elif command == "lastfm-find-tags":
            from ardj.tracks import add_missing_lastfm_tags
            add_missing_lastfm_tags()

        elif command == "mark-hitlist":
            from ardj.tracks import cmd_mark_hitlist
            cmd_mark_hitlist(*args)

        elif command == "mark-long":
            from ardj.tracks import cmd_mark_long
            cmd_mark_long(*args)

        elif command == "mark-orphans":
            from ardj.tracks import cmd_mark_orphans
            cmd_mark_orphans(*args)

        elif command == "mark-recent":
            from ardj.tracks import cmd_mark_recent
            cmd_mark_recent(*args)

        elif command == "play":
            from ardj.database import connect
            from ardj import tracks
            tracks.set_urgent(" ".join(args).decode("utf-8"))
            connect().commit()

        elif command == "loop":
            cmd_loop(*args)

        elif command == "icecast":
            from ardj.icecast import cmd_run
            cmd_run(*args)

        elif command == "icecast-config":
            from ardj.icecast import cmd_config
            cmd_config(*args)

        elif command == "ezstream":
            from ardj.ezstream import cmd_run
            cmd_run(*args)

        elif command == "ezstream-config":
            from ardj.ezstream import cmd_config
            cmd_config(*args)

        elif command == "ices":
            from ardj.ices import cmd_run
            cmd_run(*args)

        elif command == "ices-config":
            from ardj.ices import cmd_config
            cmd_config(*args)

        elif command == "log":
            from ardj.util import get_user_path, run_replace
            run_replace(["tail", "-F", get_user_path("ardj.log")])

        elif command == "worker":
            from ardj import worker
            worker.run_task(*args)

        elif command == "run":
            from ardj import get_data_path
            from ardj.util import get_exec_path, run_replace

            if not get_exec_path("screen"):
                print "GNU Screen is needed for this."
                exit(1)

            rc = get_data_path("screen.rc")

            if sys.stdout.isatty():
                command = ["screen", "-S", "ardj", "-RR", "-c", rc]
            else:
                command = ["screen", "-S", "ardj", "-d", "-m", "-c", rc]
            run_replace(command)

        elif command is None:
            print USAGE.strip()
            exit(1)

        else:
            print "Unknown command: %s; run ardj without arguments to see help." % command
            exit(1)

    except KeyboardInterrupt:
        print "Interrupted."
        exit(1)

    except Exception, e:
        print "%s: %s" % (e.__class__.__name__, e)
        print traceback.format_exc()
        exit(1)


if __name__ == "__main__":
    main(*sys.argv)
