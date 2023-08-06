# -*- coding: utf-8 -*-
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.
from logging import getLogger as get_logger
from socket import error as socket_error
from threading import Event, Thread

from six.moves.queue import Queue, Empty

from logstash_async.constants import QUEUE_CHECK_INTERVAL
from logstash_async.utils import safe_log_via_print


class LogProcessingWorker(Thread):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        self._host = kwargs.pop('host')
        self._port = kwargs.pop('port')
        self._transport = kwargs.pop('transport')
        self._ssl_enable = kwargs.pop('ssl_enable')
        self._ssl_verify = kwargs.pop('ssl_verify')
        self._keyfile = kwargs.pop('keyfile')
        self._certfile = kwargs.pop('certfile')
        self._ca_certs = kwargs.pop('ca_certs')

        super(LogProcessingWorker, self).__init__(*args, **kwargs)
        self.daemon = True
        self.name = self.__class__.__name__

        self._shutdown_event = Event()
        self._queue = Queue()

        self._cant_reach_logstash = False
        self._logger = None

    # ----------------------------------------------------------------------
    def enqueue_event(self, event):
        # called from other threads
        self._queue.put(event)

    # ----------------------------------------------------------------------
    def shutdown(self):
        # called from other threads
        self._shutdown_event.set()

    # ----------------------------------------------------------------------
    def run(self):
        self._setup_logger()
        try:
            self._process_events()
        except Exception as e:
            # we really should not get anything here, and if, the worker thread is dying
            # too early resulting in undefined application behaviour
            self._log_general_error(e)

    # ----------------------------------------------------------------------
    def _setup_logger(self):
        self._logger = get_logger(self.name)

    # ----------------------------------------------------------------------
    def _process_events(self):
        while True:
            try:
                event = self._fetch_event()
                self._transport.send(event)
                # Sending message was successful
                if self._cant_reach_logstash:
                    self._safe_log("info", "Re-established connection to logstash.")
                    self._cant_reach_logstash = False
            except Empty:
                if self._shutdown_requested():
                    return
                self._delay_processing()
            except socket_error:
                if self._shutdown_requested():
                    return
                if not self._cant_reach_logstash:
                    self._safe_log("error", ("Failed to reach logstash at %s:%s." % (self._host, self._port))
                                   + " Log messages will be lost until connection is re-established.")
                    self._cant_reach_logstash = True

    # ----------------------------------------------------------------------
    def _fetch_event(self):
        return self._queue.get(block=False)

    # ----------------------------------------------------------------------
    def _delay_processing(self):
        self._shutdown_event.wait(QUEUE_CHECK_INTERVAL)

    # ----------------------------------------------------------------------
    def _shutdown_requested(self):
        return self._shutdown_event.is_set()

    # ----------------------------------------------------------------------
    def _log_general_error(self, exc):
        self._safe_log(u'exception', u'An unexpected error occurred: %s', exc)

    # ----------------------------------------------------------------------
    def _safe_log(self, log_level, message, *args, **kwargs):
        # we cannot log via the logging subsystem any longer once it has been set to shutdown
        if self._shutdown_requested():
            safe_log_via_print(log_level, message, *args, **kwargs)
        else:
            log_func = getattr(self._logger, log_level)
            return log_func(message, *args, **kwargs)
