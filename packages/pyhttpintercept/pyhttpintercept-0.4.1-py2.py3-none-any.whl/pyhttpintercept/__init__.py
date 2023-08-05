# encoding: utf-8

# Get module version
from ._metadata import __version__, __authorshort__, __module_name__

__all__ = [
    '__version__',
    '__module_name__',
    '__authorshort__',
    'ThreadedHTTPWebServer',
    'HTTPWebServer',
    'InterceptServer',
    'BaseInterceptHandler',
    'BodyInterceptHandler',
    'ServerRootWindow',
    'ServerChildWindow',
    'ServerFrame',
    'ServerConfigRootWindow',
    'ServerConfigChildWindow',
    'ServerConfigFrame'
]

# Import key items from module
from .server import (HTTPWebServer,
                     ThreadedHTTPWebServer,
                     InterceptServer)

from .intercept.handlers import (BaseInterceptHandler,
                                 BodyInterceptHandler)

from .gui import (ServerRootWindow,
                  ServerChildWindow,
                  ServerFrame,
                  ServerConfigRootWindow,
                  ServerConfigChildWindow,
                  ServerConfigFrame)

# Set default logging handler to avoid "No handler found" warnings.
from logging import NullHandler, getLogger
getLogger(__name__).addHandler(NullHandler())
