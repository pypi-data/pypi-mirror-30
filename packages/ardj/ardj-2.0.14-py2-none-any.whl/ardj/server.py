# encoding=utf-8

"""
Web UI for ardj
"""

import hashlib
import json
import mimetypes
import os
import re
import sys
import time
import traceback

import jinja2
import web

from ardj import get_data_path
from ardj import config
from ardj.database import connect, transaction
from ardj.listeners import get_count
from ardj.log import *
from ardj.models import *
from ardj.tracks import add_vote
from ardj.util import utf, skip_current_track, format_duration, format_age, \
    get_user_path, get_music_path
from ardj.worker import add_task

import auth
import console
import tracks
import log
from users import get_admins
from util import skip_current_track


def get_web_path(path):
    return get_data_path("webroot/" + path)


def send_json(f):
    """The @send_json decorator, encodes the return value in JSON."""
    def wrapper(*args, **kwargs):
        web.header("Access-Control-Allow-Origin", "*")
        try:
            data = f(*args, **kwargs)
            if isinstance(data, (str, unicode)):
                data = {"message": data}
        except Exception, e:
            data = {
                "success": False,
            }

            n = e.__class__.__name__
            if n[0].lower() in "uaioe":
                data["message"] = "Houston, we've got an %s: %s" % (n, e)
            else:
                data["message"] = "Houston, we've got a %s: %s" % (n, e)

        if web.ctx.env["PATH_INFO"].endswith(".js"):
            var_name = "response"
            callback_name = None

            for part in web.ctx.env["QUERY_STRING"].split("&"):
                if part.startswith("var="):
                    var_name = part[4:]
                elif part.startswith("callback="):
                    callback_name = part[9:]

            web.header("Content-Type", "application/javascript; charset=UTF-8")
            if callback_name is not None:
                return "var %s = %s; %s(%s);" % (var_name, json.dumps(data), callback_name, var_name)
            return "var %s = %s;" % (var_name, json.dumps(data))
        else:
            web.header("Content-Type", "application/json; charset=UTF-8")
            return json.dumps(data, ensure_ascii=False, indent=True)
    return wrapper


class UsageError(RuntimeError):
    pass


class Templates(object):
    env = None

    @classmethod
    def get_instance(cls):
        if cls.env is None:
            folder = get_web_path("templates")
            loader = jinja2.FileSystemLoader(folder)
            cls.env = jinja2.Environment(loader=loader)
        return cls.env

    @classmethod
    def render(cls, template_name, data=None):
        if data is None:
            data = {}

        elif not isinstance(data, dict):
            raise ValueError("template data must be a dict")

        # TODO: move to config
        data["site_name"] = "ardj"

        # log_debug("Rendering template {}", template_name)

        tpl = cls.get_instance().get_template(template_name)
        return tpl.render(data)


class Controller:
    """
    Basic request handler.
    Adds exception handling and some handy methods.
    """
    def GET(self, *args):
        db = connect()
        try:
            return self.on_get(*args)
        except Exception, e:
            return self.on_exception(e)

    def POST(self, *args):
        db = connect()
        try:
            return self.on_post(*args)
        except Exception, e:
            return self.on_exception(e)

    def on_exception(self, e):
        log_exception("%s: %s -- %s" % (e.__class__.__name__, e, web.ctx.path))
        return self.unavailable(str(e) + "\n\n" + traceback.format_exc())

    def send_file(self, path):
        if not os.path.exists(path):
            log_debug("web: file {} not found", path)
            return self.notfound("file not found")

        elif not os.path.isfile(path):
            log_debug("web: {} is not a file", path)
            return self.notfound("not a file")

        ct = mimetypes.guess_type(path)[0]
        if ct == "text/html":
            ct += "; charset=utf-8"

        web.header("Content-Type", ct)
        web.ctx.status = "200 OK"

        with open(path, "rb") as f:
            return f.read()

    def send_json(self, data):
        encoded_data = json.dumps(data)

        web.header("Content-Type", "application/javascript; charset=utf-8")
        web.header("Access-Control-Allow-Origin", "*")

        return encoded_data

    def render_page(self, template, data=None, status="200 OK"):
        html = Templates.render(template, data)

        web.header("Content-Type", "text/html; charset=utf-8")
        web.ctx.status = status

        return html

    def notfound(self, message):
        web.ctx.status = "404 Not Found"
        web.header("Content-Type", "text/plain; charset=utf-8")
        return utf(message)

    def unavailable(self, message):
        web.ctx.status = "503 Service Unavailable"
        web.header("Content-Type", "text/plain; charset=utf-8")
        return utf(message)

    def get_login(self):
        """
        Returns the user name.  This should be an email, is stored in the votes
        table.  Currently this is a hash of the users ip address and user agent,
        which is kind of sufficient for local stations.  The only problem is that
        the user looks different after software upgrade, but well, OK.
        """
        remote_addr = str(web.ctx.ip)
        user_agent = web.ctx.environ.get("HTTP_USER_AGENT", "none")

        digest = hashlib.sha1(remote_addr + user_agent).hexdigest()
        user_id = "ardj+%s@umonkey.net" % digest[:16]

        return user_id

    def tracks(self, tracks):
        return [t.for_template() for t in tracks]


class DataController(Controller):
    """
    Controller which works with the database.
    Methods are executed inside a transaction.
    """
    @transaction
    def GET(self, *args):
        ts = time.time()
        path = web.ctx.path

        try:
            res = self.on_get(*args)

            dur = time.time() - ts
            if dur > 1:
                log_debug("Slow request: {} -- {} seconds.", path, dur)

            return res
        except Exception, e:
            return self.on_exception(e)

    def on_exception(self, e):
        log_exception("%s: %s -- %s" % (e.__class__.__name__, e, web.ctx.path))
        return self.unavailable(str(e) + "\n\n" + traceback.format_exc())


class JsonController(DataController):
    def on_exception(self, e):
        log_exception("{}: {}", e.__class__.__name__, str(e))
        return self.send_json({"message": str(e)})


class AuthController(Controller):
    def GET(self):
        args = web.input(token=None)
        if args.token is None:
            web.header("Content-Type", "text/plain; charset=utf-8")
            return "Please specify a token or POST."
        token = auth.confirm_token(args.token)
        if token:
            web.header("Content-Type", "text/plain; charset=utf-8")
            return "OK, tell this to your program: %s" % args.token
        else:
            web.header("Content-Type", "text/plain; charset=utf-8")
            return "Wrong token."

    @send_json
    def POST(self):
        args = web.input(id=None, type=None)
        auth.create_token(args.id, args.type)
        return {"status": "ok", "message": "You'll soon receive a message with a confirmation link."}


class StaticController(Controller):
    def on_get(self, url):
        path = get_web_path(url)
        return self.send_file(path)


class IndexController(DataController):
    def on_get(self):
        return self.render_page("index.tpl", {
            "tab": "recent",
            "tracks": self.get_recent(),
            "queue": self.get_queue(),
        })

    def get_recent(self):
        return self.tracks(Track.find_recently_played(100))

    def get_queue(self):
        return self.tracks(Track.get_queue())


class EnvController(Controller):
    def GET(self):
        text = ""
        for k, v in web.ctx.items():
            text += "%s = %s\n" % (k, utf(v))
        return text


class InfoController(Controller):
    @send_json
    def GET(self):
        args = web.input(id=None, token=None)
        sender = auth.get_id_by_token(args.token)

        track_id = args.id
        if track_id is None:
            raise RuntimeError("track id not specified")

        track = tracks.get_track_by_id(track_id, sender=sender)
        if track is None:
            raise RuntimeError("track %s not found." % track_id)

        return track


class PlaylistController(Controller):
    @send_json
    def GET(self):
        args = web.input(name="all", artist=None, tag=None)

        playlist_name = args["name"]
        if playlist_name == "bookmarks":
            playlist_name = "bm:hex@umonkey.net"

        artist_name = args["artist"]
        if artist_name == "All artists":
            artist_name = None

        tag_name = args["tag"]
        if tag_name == "All tags":
            tag_name = None

        print "Playlist query: %s" % dict(args)

        result = {"artsits": [], "tags": [], "tracks": []}
        result["artists"] = [a["name"] for a in database.Artist.query(
            playlist=playlist_name, tag=tag_name)]
        result["tags"] = database.Label.query_names(
            playlist=playlist_name, artist=artist_name)

        tracks = database.Track.query(
            playlist=playlist_name, artist=artist_name, tag=tag_name, count=None)
        result["tracks"] = [{"id": t["id"], "artist": t["artist"],
            "title": t["title"]} for t in tracks]

        return result


class QueueController(JsonController):
    def on_get(self, track_id):
        login = self.get_login()

        track = Track.get_by_id(track_id)
        if not track:
            return self.send_json({"message": "track not found"})

        track.queue("anonymous")

        return self.send_json({"success": True,
                               "message": "Track added to the queue.",
                               "trigger": "ardj.home.refresh"})


class SkipController(JsonController):
    def on_post(self):
        login = self.get_login()
        log_info("web: user {} skipped current track", login)

        skip_current_track()
        return self.send_json({"message": "OK, skipping.",
                               "trigger": "ardj.home.refresh"})


class RecentController(Controller):
    @send_json
    def GET(self):
        return {
            "success": True,
            "scope": "recent",
            "tracks": list(self.get_tracks()),
        }

    def get_tracks(self):
        for track in database.Track.find_recently_played():
            track["artist_url"] = track.get_artist_url()
            track["track_url"] = track.get_track_url()
            yield track


class RocksController(JsonController):
    vote_value = 1

    def on_post(self):
        login = self.get_login()

        track = self.get_track()
        if not track:
            return self.send_json({"message": "Nothing is playing."})

        add_vote(track["id"], login, self.vote_value)

        return self.send_json({"message": "Thanks!"})

    def get_track(self):
        """Returns the currently playing track or None"""
        for t in Track.find_recently_played(1):
            if time.time() < (t["last_played"] + t["length"]):
                return t


class SucksController(RocksController):
    vote_value = -1


class DownloadController(DataController):
    def on_get(self, track_id):
        login = self.get_login()

        track = Track.get_by_id(track_id)
        if not track:
            return self.notfound("track not found")

        path = get_user_path("music/" + utf(track["filename"]))
        if not os.path.exists(path):
            return self.notfound("file %s not found" % path)

        f = open(path, "rb")

        web.header("Content-Type", "application/octet-stream")

        fn = os.path.basename(path)
        web.header("Content-Disposition", "attachment; filename=\"%s\"" % fn)

        return f


class SearchController(Controller):
    @send_json
    def GET(self):
        args = web.input(query=None)

        track_ids = tracks.find_ids(args.query)
        track_info = [database.Track.get_by_id(id) for id in track_ids]

        return {
            "success": True,
            "scope": "search",
            "tracks": track_info,
        }


class StatusController(JsonController):
    def on_get(self):
        last = web.input(last=None).last

        db = connect()

        track = self.get_current()
        for x in range(12):
            if not last or last != str(track["id"]):
                break

            break  # long polling disabled for now, causes web ui freeze

            db.rollback()
            time.sleep(5)
            track = self.get_current()

        db.rollback()
        return self.send_json(track)

    def get_current(self):
        track_id = tracks.get_last_track_id()
        if track_id is None:
            return None

        track = tracks.get_track_by_id(track_id)
        if track is None:
            return None

        track["current_ts"] = int(time.time())
        track["listeners"] = get_count() or 0
        return track


class TagCloudController(Controller):
    @send_json
    def GET(self):
        tags = database.Track.find_tags(
            cents=4, min_count=1)
        return {"status": "ok", "tags": dict(tags)}


class TrackController(DataController):
    def on_get(self, track_id):
        track = Track.get_by_id(track_id)
        if not track:
            return self.notfound("track not found")

        t = track.for_template()
        t["labels"] = ", ".join(sorted(track.get_labels()))

        return self.render_page("track.tpl", {
            "tab": "music",
            "track": t,
        })

    def on_post(self, track_id):
        track = Track.get_by_id(track_id)
        if not track:
            return self.notfound("track not found")

        try:
            form = web.input(title="", artist="", labels="", delete=None, tagme=None)

            track["title"] = form.title
            track["artist"] = form.artist
            if form.delete == "yes":
                track["weight"] = 0
                log_info("Track %u deleted.", track["id"])
            track.put()

            add_task("tags.write:%u" % track["id"])

            labels = [l.strip() for l in form.labels.split(",")]
            track.set_labels(labels)
            connect().commit()

            next_url = "/artist/" + utf(track["artist"])

            if form.tagme == "yes":
                tracks = Track.find_by_tag("tagme", limit=1)
                if tracks:
                    next_url = "/track/%u" % tracks[0]["id"]

            return self.send_json({"message": "Changes saved.",
                                   "redirect": next_url})

        except Exception, e:
            log_exception("Error editing track: {}", e)
            return self.send_json({"message": "Error saving changes: %s" % e})


class UpdateTrackController(Controller):
    @send_json
    def POST(self):
        args = web.input(
            token=None,
            id=None,
            title=None,
            artist=None,
            tag=[])

        sender = auth.get_id_by_token(args.token)
        if sender is None:
            raise UsageError("bad token")

        track = database.Track.get_by_id(int(args.id))
        if track is None:
            raise UsageError("track not found")

        if args.artist:
            track["artist"] = args.artist
            log_debug("{0} set artist for track {1} to {2}",
                sender, args.id, args.artist)
        if args.title:
            track["title"] = args.title
            log_debug("{0} set title for track {1} to {2}",
                sender, args.id, args.title)
        track.put()

        if args.tag:
            track.set_labels(args.tag)
            log_debug("{0} set labels for track {1} to {2}",
                sender, args.id, ", ".join(args.tag))

        return {"success": True}


class UploadController(JsonController):
    def on_get(self):
        return self.render_page("upload.tpl", {
            "tab": "upload",
        })

    def on_post(self):
        labels = web.input().get("labels", "music, tagme")
        labels = re.split('[,\s+]', labels)

        tmp_label = "just_added"
        labels.append(tmp_label)

        Label.delete_by_name(tmp_label)

        accepted, ignored = 0, 0
        for file in self.get_files():
            if not re.match(r'.*\.(mp3|ogg|ogv|oga|flac)$', file.filename):
                log_debug("File {} ignored -- unsupported type.", file.filename)
                ignored += 1

            else:
                dst = get_music_path(utf(file.filename))
                if os.path.exists(dst):
                    os.unlink(dst)

                with open(dst, "wb") as f:
                    f.write(file.value)
                    log_info("File {} written.", dst)

                t = tracks.add_file(dst, labels)
                accepted += 1

        message = u"%u files accepted, %u ignored.  Thanks!" % (accepted, ignored)
        return self.send_json({"message": message})

    def get_files(self):
        files = web.webapi.rawinput().get("file")
        if not isinstance(files, list):
            files = [files]
        for file in files:
            yield file


class PlaylistController(DataController):
    def on_get(self):
        path = self.get_path()
        with open(path, "rb") as f:
            contents = f.read()

        return self.render_page("playlist.tpl", {
            "tab": "playlist",
            "contents": contents,
            "editable": os.access(path, os.W_OK),
        })

    @send_json
    def on_post(self):
        contents = web.input(contents="").contents
        if not contents:
            return "Sorry, Dave.  I'm afraid I can't do that."

        path = self.get_path()
        with open(path, "wb") as f:
            f.write(contents)
            log_info("Wrote new playlists file.")

        return "Done.  Effective immediately."

    def get_path(self):
        from ardj.playlist import get_playlist_path
        return get_playlist_path()


def get_application():
    app = web.application((
        r"/", IndexController,
        r"/env", EnvController,

        r"/playlist", PlaylistController,
        r"/track/(\d+)", TrackController,
        r"/track/(\d+)/queue", QueueController,
        r"/track/(\d+)/download", DownloadController,
        r"/api/rocks", RocksController,
        r"/api/sucks", SucksController,
        r"/api/skip", SkipController,
        r"/status\.json", StatusController,
        r"/upload", UploadController,

        r"/((?:docs|fonts|scripts|styles|images)/.+)", StaticController,

        r"/auth(?:\.json)?", AuthController,
        r"/playlist\.json", PlaylistController,
        r"/tag/cloud\.json", TagCloudController,
        r"/track/search\.json", SearchController,
        r"/track/update\.json", UpdateTrackController,
    ))

    return app


def serve_http(hostname, port):
    """Starts the HTTP web server at the specified socket."""
    sys.argv.insert(1, "%s:%s" % (hostname, port))

    log_info("Starting the ardj web service at http://{}:{}/", hostname, port)

    app = get_application()
    app.run()


def cmd_create_token(email=None, *args):
    """Create a new token for the specified email address."""
    if email is None:
        raise RuntimeError("Please specify email address.")

    from auth import create_token
    token = create_token(email, "email")
    print "New token: %s (needs activation)." % token["token"]


def cmd_serve(arg=None, *args):
    if arg == "help":
        print "Runs the local web server which is used to administer the radio,"
        print "also to accept user votes."
        exit(1)

    elif arg is not None:
        print "This command takes no argument."
        exit(1)

    os.chdir("/")

    socket = config.get("web_socket", "0.0.0.0:8080")
    serve_http(*socket.split(":", 1))


def cmd_tokens():
    """List valid tokens."""
    from ardj.auth import get_active_tokens
    for t in get_active_tokens():
        print "%s: %s" % (t["login"], t["token"])
