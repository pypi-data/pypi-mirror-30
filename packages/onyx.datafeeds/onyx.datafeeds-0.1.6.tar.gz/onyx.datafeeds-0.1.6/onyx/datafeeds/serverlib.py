###############################################################################
#
#   Copyright: (c) 2017 Carlo Sbraccia
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
###############################################################################

from onyx.core import load_system_configuration
from onyx.core import Date
from onyx.core import CurveField, HlocvCurveField, GCurveField

from .utils import encode_message, decode_message

from .exceptions import DatafeedError, DatafeedFatal, SecurityError, FieldError
from .bloomberg import blp_api as bbg_api

from concurrent import futures

import tornado.ioloop
import tornado.tcpserver
import tornado.httpclient
import tornado.gen
import tornado.netutil

import time
import json
import datetime
import socket
import urllib
import logging

__all__ = ["DataServer"]

API_ERRORS = DatafeedError, SecurityError, FieldError, NotImplementedError
REREGISTER = 60000*2  # check registration every 2 minutes


# -----------------------------------------------------------------------------
def cycle(elements):
    while True:
        for element in elements:
            yield element


# -----------------------------------------------------------------------------
def bdp_request(bdp_clt, timeout, request):
    try:
        data = bdp_clt.fetch(timeout=timeout, **request)
        return {
            "type": type(data).__name__,
            "payload": data,
        }
    except API_ERRORS as err:
        return {
            "type": type(err).__name__,
            "payload": str(err),
        }


# -----------------------------------------------------------------------------
def bdh_request(timeout, request):
    try:
        data = bbg_api.BbgBDH(timeout=timeout, **request)
        return {
            "type": type(data).__name__,
            "payload": data,
        }
    except API_ERRORS as err:
        return {
            "type": type(err).__name__,
            "payload": str(err),
        }


# -----------------------------------------------------------------------------
def process_response(resp):
    dtype = resp["type"]
    if dtype == "Curve":
        resp["payload"] = CurveField.to_json(None, resp["payload"])
    elif dtype == "HlocvCurve":
        resp["payload"] = HlocvCurveField.to_json(None, resp["payload"])
    elif dtype == "GCurve":
        resp["payload"] = GCurveField.to_json(None, resp["payload"])
    return resp


###############################################################################
class DataServer(tornado.tcpserver.TCPServer):
    # -------------------------------------------------------------------------
    def __init__(self, logger=None, nthreads=10, blp_timeout=1, tcp_timeout=5):
        super().__init__()
        self.logger = logger or logging.getLogger(__name__)
        self.tpool = futures.ThreadPoolExecutor(max_workers=nthreads)
        self.blp_timeout = blp_timeout * 1000  # seconds to milliseconds
        self.tcp_timeout = datetime.timedelta(seconds=tcp_timeout)
        self.bdp_clients = cycle([bbg_api.bdp_client()
                                  for thread in range(nthreads)])

    # -------------------------------------------------------------------------
    def start(self, router_addr=None, router_port=None, stop_at=None):
        config = load_system_configuration()
        router_addr = router_addr or config.get("datafeed", "router_address")
        router_port = router_port or config.getint("datafeed", "router_port")

        # --- connect to a random port from the available pool
        sockets = tornado.netutil.bind_sockets(0, address="")
        self.add_sockets(sockets)

        # --- get the port and add a callback to notify periodically that
        #     this server is available
        port = sockets[0].getsockname()[1]

        # --- create the request object used to notify the router that this
        #     server is available
        self.subreq = tornado.httpclient.HTTPRequest(
            "http://{0!s}:{1!s}/register/".format(router_addr, router_port),
            method="PUT",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            body=urllib.parse.urlencode({
                "address": socket.gethostbyname(socket.gethostname()),
                "port": port}),
            request_timeout=self.tcp_timeout.seconds
        )

        ioloop = tornado.ioloop.IOLoop.current()
        ioloop.add_callback(self.subscribe_to_router)
        tornado.ioloop.PeriodicCallback(
            self.subscribe_to_router, REREGISTER, ioloop).start()

        if stop_at is not None:
            seconds = (stop_at - Date.now()).seconds
            ioloop.call_later(seconds, lambda: self.stop_server())

        try:
            ioloop.start()
        except KeyboardInterrupt:
            self.stop_server()

    # -------------------------------------------------------------------------
    def stop_server(self):
        # --- first stop the threadpool
        self.tpool.shutdown(wait=True)
        # --- then stop the tornado event loop
        ioloop = tornado.ioloop.IOLoop.current()
        ioloop.stop()
        self.logger.info("shutting down server")

    # -------------------------------------------------------------------------
    @tornado.gen.coroutine
    def with_timeout(self, future):
        generator = yield tornado.gen.with_timeout(self.tcp_timeout, future)
        return generator

    # -------------------------------------------------------------------------
    @tornado.gen.coroutine
    def handle_stream(self, stream, address):
        # --- use time.time to monitor time needed to process request
        t_start = time.time()

        self.logger.debug("connection received from {0!s}".format(address))

        try:
            request = yield self.with_timeout(stream.read_until(b"\n"))
        except (tornado.iostream.StreamClosedError, tornado.gen.TimeoutError):
            self.logger.error("couldn't read "
                              "request from {0!s}".format(address))
            return

        request = decode_message(request)
        self.logger.debug("processing request {0!s}".format(request))

        request_type = request.pop("type")

        # --- overrides, which are sent by clients as json strings, are decoded
        #     here 'in-place'
        request["overrides"] = json.loads(request["overrides"])

        # --- try processing the request for a maximum of 5 times using
        #     geometrically increasing timeouts
        timeout = self.blp_timeout
        for k in range(5):
            self.logger.debug("timeout set to {0:d}".format(timeout))
            try:
                if request_type == "BDP":
                    # --- pull a bbg-bdp client from the clients pool
                    clt = next(self.bdp_clients)
                    resp = yield self.tpool.submit(bdp_request,
                                                   clt, timeout, request)
                else:
                    resp = yield self.tpool.submit(bdh_request,
                                                   timeout, request)
                break
            except TimeoutError:
                timeout *= 2
                self.logger.info("request {0!s} "
                    "timeout increased to {1:f}ms".format(request, timeout))
            except DatafeedFatal as err:
                # --- unrecoverable bloomberg error: don't send a reply so that
                #     the datafeed router knows this server is currently unable
                #     to respond to requests.
                self.logger.error(err, exc_info=True)
                return

        else:
            timeout /= 2
            resp = {
                "type": "TimeoutError",
                "payload": ("request timed out after 5 attempts with a final "
                            "timeout of {0!s} milliseconds").format(timeout),
            }

        resp = process_response(resp)
        resp = encode_message(resp)

        try:
            yield self.with_timeout(stream.write(resp))
        except (tornado.gen.TimeoutError, tornado.iostream.StreamClosedError):
            self.logger.error("couldn't "
                "send resp to {0!s}".format(address))
            return

        time_total = (time.time() - t_start)*1000.0
        self.logger.info("request {0!s} "
            "processed in {1:f}ms".format(request, time_total))

    # -------------------------------------------------------------------------
    @tornado.gen.coroutine
    def subscribe_to_router(self):
        # --- register only if bloomberg service is available
        active = bbg_api.test_bbg_data_service()
        if not active:
            self.logger.info("couldn't register server "
                "with router: bloomberg service currently unavailable")
            return

        self.logger.debug("trying to register "
            "with datafeed router on {0!s}".format(self.subreq.url))

        client = tornado.httpclient.AsyncHTTPClient()
        try:
            res = yield client.fetch(self.subreq)
        except ConnectionRefusedError:
            self.logger.info("couldn't register with datafeed router "
                "on {0!s}: connection refused".format(self.subreq.url))
            return
        except tornado.httpclient.HTTPError as err:
            self.logger.info("couldn't register with "
                "datafeed router on {0!s}: {1!s}".format(self.subreq.url, err))
            return

        if res.code == 201:
            self.logger.info("router accepted subscription")
        elif res.code == 205:
            # --- server already registered with router
            pass
        else:
            raise res.error
