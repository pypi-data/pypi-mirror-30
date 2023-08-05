# encoding=utf-8

"""
uWSGI module for ardj.
"""

from ardj.server import get_application
application = get_application().wsgifunc()
