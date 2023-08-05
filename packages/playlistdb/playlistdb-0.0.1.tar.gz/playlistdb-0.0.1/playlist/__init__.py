"""playlist: Keep track of on disk playlists.


Copyright (c) 2017 Jeroen F.J. Laros <jlaros@fixedpoint.nl>

Licensed under the MIT license, see the LICENSE file.
"""
from .playlist import PlayDB


__version_info__ = ('0', '0', '1')

__version__ = '.'.join(__version_info__)
__author__ = 'LUMC, Jeroen F.J. Laros'
__contact__ = 'jlaros@fixedpoint.nl'
__homepage__ = 'https://fixedpoint.nl'

usage = __doc__.split('\n\n\n')


def doc_split(func):
    return func.__doc__.split('\n\n')[0]


def version(name):
    return '{} version {}\n\nAuthor   : {} <{}>\nHomepage : {}'.format(
        name, __version__, __author__, __contact__, __homepage__)
