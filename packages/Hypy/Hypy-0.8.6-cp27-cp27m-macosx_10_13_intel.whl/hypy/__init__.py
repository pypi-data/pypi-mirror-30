"""Hypy - Pythonic Hyper Estraier"""
from hypy.lib import (PutFailed,
    OpenFailed,
    CloseFailed,
    EditFailed,
    FlushFailed,
    HCondition,
    HDatabase,
    HResults,
    HDocument,
    HHit,
    )

from hypy._version import __version__

(__version__,
PutFailed, OpenFailed, CloseFailed, EditFailed, FlushFailed,
HCondition, HDatabase, HResults, HDocument, HHit) # for pyflakes
