# encoding: utf-8

import threading
import logging_helper
from networkutil.addressing import get_my_addresses

logging = logging_helper.setup_logging()


class Shared(object):

    def __init__(self,
                 request,
                 uri=None):

        self._request = request

        self.client_address = request.client_address

        # Save the request parameters
        self.request_headers = request.headers
        self.request_protocol = None  # Will be set by self.request_uri
        self.request_host = None  # Will be set by self.request_uri
        self.request_path = None  # Will be set by self.request_uri
        self.request_uri = uri if uri is not None else u'{host}{path}'.format(host=self.request_headers[u'Host'],
                                                                              path=request.path)

    # Properties
    @property
    def _request_address(self):
        return self.request_host.split(u':')[0]

    @property
    def _addressed_to_self(self):
        return self._request_address in get_my_addresses()
        # TODO: Add ability to configure & check server aliases

    @property
    def request_uri(self):
        return u'{protocol}://{host_port}{path}'.format(protocol=self.request_protocol,
                                                        host_port=self.request_host,
                                                        path=self.request_path)

    @request_uri.setter
    def request_uri(self, value):

        try:
            protocol, uri = value.split(u'://')

        except ValueError:
            protocol = u'http'  # TODO: we are assuming! can we determine any other way?
            uri = value

        try:
            host, path = uri.split(u'/', 1)

        except ValueError:
            host = uri
            path = u'/'

        self.request_protocol = protocol
        self.request_host = host
        self.request_path = u'/{path}'.format(path=path)

    @property
    def thread(self):
        thread = threading.currentThread().name
        return thread if thread else u'?'

    # Log message formatters
    def prefix_message(self,
                       msg):
        return u'HTTP {type} ({thread}): {msg}'.format(type=self._request.command.upper(),
                                                       thread=self.thread,
                                                       msg=msg)

    def _get_debug_separator(self,
                             section):
        return self.prefix_message(u'=========================== '
                                   u'{section} '
                                   u'==========================='.format(section=section))
