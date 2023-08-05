# encoding: utf-8

from uiutil import PersistentField
from uiutil.helper.persist import get_default_global_ui_persistence_store
from configurationutil import cfg_params
from .._constants import SERVER_THREADING_KEY
from .._metadata import __version__, __authorshort__, __module_name__

# Register Config details (These are expected to be overwritten by an importing app)
cfg_params.APP_NAME = __module_name__
cfg_params.APP_AUTHOR = __authorshort__
cfg_params.APP_VERSION = __version__


get_default_global_ui_persistence_store()

server_threading = PersistentField(key=SERVER_THREADING_KEY,
                                   initial_value=True)
