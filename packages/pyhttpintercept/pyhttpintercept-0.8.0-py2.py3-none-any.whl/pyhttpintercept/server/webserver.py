# encoding: utf-8

import socket
import logging_helper
from http.server import HTTPServer
from threading import currentThread, Thread
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
from timingsutil import Timeout
from ..intercept import InterceptScenario
from .request import RequestHandler

logging = logging_helper.setup_logging()


class WebServer(HTTPServer, object):

    # TODO: Create some request thread cleanup when we are short of available threads in the pool!

    def __init__(self,
                 server_address,
                 request_handler_class=RequestHandler,
                 threads=cpu_count(),
                 # request_threads is probably excessive however when keep-alive is set on
                 # a request the thread is consumed until the connection gets closed!
                 request_threads=100,
                 threading=True):

        """Constructor.  May be extended, do not override."""

        self.port = server_address[-1]
        self._threading = threading  # Denotes whether server will run requests in serial (False) / parallel (True)!

        if self._threading:
            logging.info(u'Request threading Enabled!')

        self.pool = ThreadPool(processes=threads if threads > 1 else 2)
        self.request_pool = ThreadPool(processes=request_threads)
        self.open_requests = []

        HTTPServer.__init__(self,
                            server_address=server_address,
                            RequestHandlerClass=request_handler_class,
                            bind_and_activate=False)

        self.timeout = 5

        self.__stop = True

        # Initialise scenario config.
        self.scenarios = InterceptScenario()

    def start(self):

        logging.info(u'Starting HTTP Server on port {port}'.format(port=self.port))

        self.__stop = False

        try:
            # Load active intercept scenario.
            self.scenarios.load_active_scenario()

            self.server_bind()
            self.server_activate()

        except Exception as err:

            self.server_close()

            logging.exception(err)
            logging.error(u'HTTP Server on port {port} failed to start'.format(port=self.port))

            self.__stop = True

        if not self.__stop:
            logging.info(u'HTTP Server started on port {port}!'.format(port=self.port))

            # Run Main loop
            self.pool.apply_async(func=self.__main_loop)

    def stop(self):

        logging.info(u'Stopping HTTP Server on port {port}. Waiting for '
                     u'processes to complete...'.format(port=self.port))

        # Signal loop termination
        self.__stop = True

        try:
            # Signal server termination
            self.shutdown()  # Trigger server shutdown
            self.server_close()  # Make sure the server is closed (socket gets closed)
            logging.debug(u'HTTP Server shutting down on port {port}'.format(port=self.port))

        except Exception as err:
            logging.warning(u'HTTP Server was not started or failed to '
                            u'shut down properly on port {port}'.format(port=self.port))
            logging.warning(err)

        # Close the thread pool
        self.pool.close()
        self.request_pool.close()

        # Put the join in a separate thread so we can time it out if required!
        t_main = Thread(target=self.pool.join)
        t_main.start()

        t_req = Thread(target=self.request_pool.join)
        t_req.start()

        # Setup up a shutdown timeout so we can force exit if server does not gracefully close by itself!
        timer = Timeout(30)
        terminated = False

        # Wait for running processes to complete (pool.join is done)
        while t_main.is_alive() or t_req.is_alive():
            if timer.expired and not terminated:
                # Timer has expired so forcibly terminate the thread pool!
                logging.warning(u'Shutdown timer expired, terminating...')

                if t_main.is_alive():
                    self.pool.terminate()

                if t_req.is_alive():
                    self.request_pool.terminate()

                # Force any open request sockets to shutdown.
                # This is useful when a keep-alive connection is stuck waiting on self.rfile.readline()!
                for r in self.open_requests:
                    r.connection.shutdown(socket.SHUT_RDWR)

                terminated = True

        logging.info(u'HTTP Server stopped on port {port}'.format(port=self.port))

    def __main_loop(self):

        logging.debug(u'main loop ({t})'.format(t=currentThread().name))

        try:
            self.serve_forever()

        except Exception as err:
            logging.error(err)

        while not self.__stop:
            pass  # Run until stop requested!

    @property
    def active(self):
        return not self.__stop

    def process_request(self, request, client_address):

        if self._threading:
            self.request_pool.apply_async(func=self.process_request_threaded,
                                          args=(request, client_address))

        else:
            super(WebServer, self).process_request(request, client_address)

    def process_request_threaded(self, request, client_address):

        """Same as in BaseServer.process_request but as a thread.

        In addition, we add some exception handling!

        """

        try:
            self.finish_request(request, client_address)

        except socket.error:
            self.handle_error(request, client_address)

        finally:
            self.shutdown_request(request)
