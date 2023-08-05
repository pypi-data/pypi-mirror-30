# Copyright (c) 2018, Neil Booth
#
# All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


__all__ = ('ClientSession', 'ServerSession', 'Server')


import asyncio
import logging
import ssl
import time

from .framing import NewlineFramer
from .jsonrpc import JSONRPCv2
from .rpc import RPCProcessor, RPCRequest, RPCRequestOut, RPCBatchOut
from .util import Scheduler


class SessionBase(asyncio.Protocol):

    def __init__(self, rpc_protocol=None, framer=None, scheduler=None,
                 loop=None, logger=None):
        self.loop = loop or asyncio.get_event_loop()
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        rpc_protocol = rpc_protocol or self.default_rpc_protocol()
        self.rpc = RPCProcessor(rpc_protocol, self, logger=logger)
        self.framer = framer or self.default_framer()
        if scheduler is None:
            self.scheduler = Scheduler(self.loop, logger=self.logger)
            self.my_scheduler = True
        else:
            if scheduler.loop != self.loop:
                raise ValueError('scheduler and session have different loops')
            self.scheduler = scheduler
            self.my_scheduler = False
        self.transport = None
        self.runner = None
        # Set when a connection is made
        self._address = None
        # For logger.debug messsages
        self.verbosity = 0
        # Session ID is set on connection
        self.session_id = None
        # Statistics.  The RPC object also keeps its own statistics.
        self.start_time = time.time()
        self.send_count = 0
        self.send_size = 0
        self.last_send = self.start_time
        self.recv_count = 0
        self.recv_size = 0
        self.last_recv = self.start_time
        # Amount of bandwidth equal to 1 second of CPU time
        self.bw_unit_cost = 1000000

    def _close(self):
        # Cancel all RPC requests and all scheduler jobs, if it's ours
        for request in self.all_requests():
            request.cancel()
        if self.my_scheduler:
            self.scheduler.cancel_all()

    def data_received(self, framed_message):
        '''Called by asyncio when a message comes in.'''
        if self.verbosity >= 4:
            self.logger.debug(f'Received framed message {framed_message}')
        self.recv_size += len(framed_message)
        self.runner.cost += len(framed_message) / self.bw_unit_cost

        count = 0
        try:
            for message in self.framer.messages(framed_message):
                count += 1
                self.rpc.message_received(message)
        except MemoryError as e:
            self.logger.warning(str(e))

        if count:
            self.recv_count += count
            self.last_recv = time.time()

    def send_message(self, message):
        '''Send a message over the connection. It is framed before sending.'''
        if message:
            self.send_messages((message, ))

    def send_messages(self, messages):
        '''Send messages (a tuple or list) over the connection.

        They are framed before sending.'''
        framed_message = self.framer.frame(messages)
        self.send_size += len(framed_message)
        self.runner.cost += len(framed_message) / self.bw_unit_cost
        self.send_count += len(messages)
        self.last_send = time.time()
        if self.verbosity >= 4:
            self.logger.debug(f'Sending framed message {framed_message}')
        self.transport.write(framed_message)

    def peer_address(self):
        '''Returns the peer's address (Python networking address), or None if
        no connection or an error.

        This is the result of socket.getpeername() when the connection
        was made.
        '''
        return self._address

    def peer_address_str(self):
        '''Returns the peer's address as a human-readable string.'''
        if not self._address:
            return 'unknown'
        ip_addr_str, port = self._address[:2]
        if ':' in ip_addr_str:
            return f'[{ip_addr_str}]:{port}'
        else:
            return f'{ip_addr_str}:{port}'

    # External API
    def default_rpc_protocol(self):
        '''Return a default rpc helper if the user provides none.'''
        return JSONRPCv2

    def default_framer(self):
        '''Return a default framer.'''
        return NewlineFramer()

    def add_job(self, job):
        self.scheduler.add_job(job, self.runner)

    def add_coroutine(self, coro, on_done):
        self.scheduler.add_coroutine(coro, on_done, self.runner)

    def create_task(self, coro, on_done):
        return self.scheduler.create_task(coro, on_done, self.runner)

    def connection_made(self, transport):
        '''Called by asyncio when a connection is established.

        Derived classes overriding this method must call this first.'''
        self.transport = transport
        # This would throw if called on a closed SSL transport.  Fixed
        # in asyncio in Python 3.6.1 and 3.5.4
        self._address = transport.get_extra_info('peername')
        self.runner = self.scheduler.new_runner()

    def connection_lost(self, exc):
        '''Called by asyncio when the connection closes.'''
        self.logger.debug(f'connection lost to {self.peer_address_str()}')
        self.scheduler.remove_runner(self.runner)
        self.runner = None
        self._close()

    # App layer
    def is_closing(self):
        '''Return True if the connection is closing.'''
        return self.transport and self.transport.is_closing()

    def close(self):
        '''Close the connection.'''
        # Let connection_lost call self._close()
        if self.transport:
            self.transport.close()
        else:
            self._close()

    def abort(self):
        '''Cut the connection abruptly.'''
        if self.transport:
            self.transport.abort()

    def send_request(self, method, args=None, on_done=None, *, timeout=None):
        '''Send an RPC request over the network.'''
        request = RPCRequestOut(method, args, on_done, loop=self.loop)
        self.rpc.send_request(request)
        if timeout is not None:
            self.set_timeout(request, timeout)
        return request

    def send_notification(self, method, args=None):
        '''Send an RPC notification over the network.'''
        request = RPCRequest(method, args, None)
        self.rpc.send_request(request)
        return request

    def new_batch(self):
        return RPCBatchOut(loop=self.loop)

    def send_batch(self, batch, on_done=None, *, timeout=None):
        self.rpc.send_batch(batch, on_done)
        if timeout is not None:
            self.set_timeout(batch, timeout)
        return batch

    def set_timeout(self, request, delay):
        '''Cause a request (or batch request) to time-out after delay
        seconds (a float).'''
        if request not in self.rpc.all_requests():
            raise RuntimeError(f'cannot set a timeout on {request} - it does '
                               'not belong to this session')

        def on_timeout():
            msg = f'{request} timed out after {delay}s'
            request.set_exception(asyncio.TimeoutError(msg))

        def on_done(request):
            handle.cancel()

        handle = self.loop.call_later(delay, on_timeout)
        request.add_done_callback(on_done)

    def all_requests(self):
        '''Returns a list of all requests that have not yet completed.

        If a batch requests is outstanding, it is returned and not the
        individual requests it is comprised of.
        '''
        return self.rpc.all_requests()

    def notification_handler(self, method):
        '''Return the handler for the given notification.

        The handler can be synchronous or asynchronous.'''
        return None

    def request_handler(self, method):
        '''Return the handler for the given request method.

        The handler can be synchronous or asynchronous.'''
        return None


class ClientSession(SessionBase):
    '''A client session.

    To initiate a connection to the remote server call
    create_connection().  Each successful call should have a
    corresponding call to close().

    Alternatively if used in a with statement, the connection is made
    on entry to the block, and closed on exit from the block.
    '''

    def __init__(self, host=None, port=None, *, rpc_protocol=None, framer=None,
                 scheduler=None, loop=None, logger=None, proxy=None, **kwargs):
        super().__init__(rpc_protocol, framer, scheduler, loop, logger)
        self.host = host
        self.port = port
        self.kwargs = kwargs
        self.proxy = proxy

    async def create_connection(self):
        '''Initiate a connection.'''
        self_func = lambda: self
        if self.proxy:
            return await self.proxy.create_connection(
                self_func, self.host, self.port, loop=self.loop, **self.kwargs)

        return await self.loop.create_connection(
            self_func, self.host, self.port, **self.kwargs)

    async def __aenter__(self):
        await self.create_connection()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.close()


class ServerSession(SessionBase):
    '''A server session - created by a listening Server for each incoming
    connection.'''


class Server(object):
    '''A simple wrapper around an asyncio.Server object.'''

    def __init__(self, session_factory, host=None, port=None, *,
                 loop=None, **kwargs):
        self.host = host
        self.port = port
        self.loop = loop or asyncio.get_event_loop()
        self.server = None
        self._session_factory = session_factory
        self._kwargs = kwargs
        self._sessions = set()

    async def listen(self):
        self.server = await self.loop.create_server(
            self._session_factory, self.host, self.port, **self._kwargs)

    async def wait_closed(self):
        if self.server:
            await self.server.wait_closed()

    def close(self):
        '''Close the listening socket.  This does not close any ServerSession
        objects created to handle incoming connections.
        '''
        if self.server:
            self.server.close()
            self.server = None
