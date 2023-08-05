# encoding=utf-8

import json
import urllib
import urllib2
import urlparse

from ardj.log import *
from ardj.util import utf


__all__ = ["fetch_url", "fetch_url_json"]


def get_opener(url, user, password):
    """Returns an opener for the url.

    Builds a basic HTTP auth opener if necessary."""
    opener = urllib2.urlopen

    if user or password:
        pm = urllib2.HTTPPasswordMgrWithDefaultRealm()
        pm.add_password(None, url, user, password)

        ah = urllib2.HTTPBasicAuthHandler(pm)
        opener = urllib2.build_opener(ah).open

    return opener


def parse_url_auth(url, user, password):
    """Extracts auth parameters from the url."""
    up = urlparse.urlparse(url)

    netloc = up.netloc
    if "@" in up.netloc:
        auth, netloc = up.netloc.split("@", 1)
        user, password = list(auth.split(":", 1) + [password])[:2]

    result = "%s://%s%s" % (up.scheme, netloc, up.path)
    if up.query:
        result += "?" + up.query
    return result, user, password


def fetch_url(url, args=None, user=None, password=None, quiet=False, post=False, retry=3):
    """Retrieves a file over HTTP.

    Arguments:
    url -- the file to retrieve.
    args -- a dictionary of query parameters
    user, password -- enable HTTP basic auth
    """
    if type(url) != str:
        raise TypeError("URL must be a string.")

    if args and not post:
        url += '?' + urllib.urlencode(args)

    url, user, password = parse_url_auth(url, user, password)

    opener = get_opener(url, user, password)
    try:
        if post:
            if not quiet:
                log_debug('Posting to {}', utf(url))
            u = opener(urllib2.Request(url), urllib.urlencode(args))
        else:
            if not quiet:
                log_debug('Downloading {}', utf(url))
            u = opener(urllib2.Request(url), None)

        return u.read()

    except Exception, e:
        if retry:
            log_error('Could not fetch {}: {} (retrying)', utf(url), e)
            return fetch_url(url, args, user, password, quiet, post, retry - 1)

        log_error('Could not fetch {}: {}', utf(url), e)
        raise


def fetch_url_json(*args, **kwargs):
    """Fetches the data using fetch(), parses it using the json module, then
    returns the result."""
    data = fetch_url(*args, **kwargs)
    if data is not None:
        return json.loads(data)
