#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = [
    '__author__', '__email__', '__version__', '__qtversion__',
    'VERSION', 'QTVERSION', 'Config', 'Location', 'LocationError',
    'configure', 'get_config', 'get_writable_path', 'get_standard_paths',
]

from .base import (
    Config, Location, LocationError, configure, get_config,
    _get_implementation,
)

VERSION = (0, 3, 2)
QTVERSION = (5, 4, 1)

__author__ = 'Tzu-ping Chung'
__email__ = 'uranusjr@gmail.com'
__version__ = '.'.join(str(i) for i in VERSION)

__qtversion__ = '.'.join(str(i) for i in QTVERSION)


def get_writable_path(location, config=None):
    """Get the directory where files of type should be written to. A
    :class:`.LocationError` is raised if the location cannot be determined.

    :rtype: :class:`pathlib.Path`

    .. note::
        The storage location returned can be a directory that does not exist;
        i.e., it may need to be created by the system or the user.
    """
    if not isinstance(location, Location):
        location = Location[str(location)]
    return _get_implementation().get_writable_path(
        location=location, config=config,
    )


def get_standard_paths(location, config=None):
    """Get all the directories where files of type belong.

    The list of directories is sorted from high to low priority, starting with
    :func:`.get_writable_path` if it can be determined. This list is empty if
    no locations for type are defined.

    :rtype: :class:`pathlib.Path`

    .. seealso::
        :func:`.get_writable_path`.
    """
    if not isinstance(location, Location):
        location = Location[str(location)]
    return _get_implementation().get_standard_paths(
        location=location, config=config,
    )
