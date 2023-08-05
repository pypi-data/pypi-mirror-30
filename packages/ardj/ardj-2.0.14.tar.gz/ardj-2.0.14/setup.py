#!/usr/bin/env python
# vim: set fileencoding=utf-8 nofoldenable:

from setuptools import setup


VERSION = "2.0.14"

classifiers = [
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Natural Language :: English',
    'Operating System :: Unix',
    'Programming Language :: Python',
    'Topic :: Internet',
    ]

PACKAGE_DATA = {
    "ardj": ["data/*.sql",
             "data/*.mp3",
             "data/*.ogg",
             "data/screen.rc",
             "data/webroot/*.html",
             "data/webroot/favicon.ico",
             "data/webroot/docs/*.html",
             "data/webroot/fonts/*",
             "data/webroot/images/*",
             "data/webroot/scripts/*",
             "data/webroot/styles/*",
             "data/webroot/templates/*.tpl"],
}

LONG_DESC = """Wraps around icecast2 and ezstream (or ices0) to create a radio station with possibly very complicated playlist system.
Configures icecast2 and ezstream automatically, so you don't have to.
Playlists can be very simple, like a shuffle, or complicated, with time slots, jingles and prerolls.
Includes a simple web UI to operate the radio.
"""


setup(
    name = 'ardj',
    version = VERSION,
    author = 'Justin Forest',
    author_email = 'hex@umonkey.net',
    url = 'http://umonkey.net/ardj/',

    packages = ['ardj'],
    package_dir = {'ardj': 'src/ardj'},
    package_data = PACKAGE_DATA,
    scripts = ['bin/ardj', 'bin/ardj-next', 'bin/ardj-ezmeta'],

    install_requires = ['PyYAML', 'mutagen', 'oauth2', 'web.py', 'Jinja2', 'mysql', 'setuptools'],

    classifiers = classifiers,
    description = 'An artificial DJ for you internet radio.',
    long_description = LONG_DESC,
    license = 'GNU GPL',
)
