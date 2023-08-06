"""
trip.adapters
~~~~~~~~~~~~~

This module contains the transport adapters that Trip uses to define
and maintain connections.

The following is the connections between Trip and Tornado:
    tcpclient.TCPClient                     -> TCPClient
    simple_httpclient.SimpleAsyncHTTPClient -> HTTPAdapter
    simple_httpclient._HTTPConnection       -> HTTPConnection
    http1connection.HTTP1Connection         -> HTTP1Connection
    
"""

import os, sys, functools, socket, collections
from io import BytesIO
from weakref import ref

from tornado import gen, stack_context
from tornado.concurrent import Future
from tornado.http1connection import (
    HTTP1Connection as _HTTP1Connection,
    HTTP1ConnectionParameters,
    _ExceptionLoggingContext, _GzipMessageDelegate)
from tornado.httputil import (
    parse_response_start_line, 
    HTTPMessageDelegate, HTTPInputError, RequestStartLine)
from tornado.ioloop import IOLoop
from tornado.iostream import StreamClosedError, IOStream
from tornado.log import app_log, gen_log
from tornado.platform.auto import set_close_exec
from tornado.netutil import Resolver, OverrideResolver
from tornado.tcpclient import TCPClient as _TCPClient, _Connector

from requests.adapters import BaseAdapter
from requests.compat import urlsplit, urlparse
from requests.exceptions import HTTPError
from requests.utils import (
    DEFAULT_CA_BUNDLE_PATH,
    prepend_scheme_if_needed, 
    get_auth_from_url, select_proxy)

from .compat import BadStatusLine, LineTooLong
from .contrib.socks import SockIOStream
from .exceptions import Timeout
from .utils import get_host_and_port, get_proxy_headers, parse_timeout


class TCPClient(_TCPClient):
    """ override tcpclient to enable https proxy. """

    def _create_stream(self, max_buffer_size, af, addr, source_ip=None,
            source_port=None):
        # Always connect in plaintext; we'll convert to ssl if necessary
        # after one connection has completed.
        source_port_bind = source_port if isinstance(source_port, int) else 0
        source_ip_bind = source_ip

        socket_obj = socket.socket(af)
        set_close_exec(socket_obj.fileno())
        try:
            stream = IOStream(socket_obj,
                              io_loop=self.io_loop,
                              max_buffer_size=max_buffer_size)

            # connect proxy
            if source_port_bind or source_ip_bind:
                @gen.coroutine
                def _(addr):
                    proxy_headers = get_proxy_headers(source_ip_bind)
                    parsed = urlparse(source_ip_bind)
                    scheme, host, port = parsed.scheme, parsed.hostname, source_port_bind
                    if 'socks' in scheme:
                        r = yield self._negotiate_socks(addr, (source_ip_bind, source_port_bind))
                        raise gen.Return(r)
                    elif scheme in ('http', 'https'):
                        r = yield stream.connect((host, port))
                        if scheme == 'https':
                            yield self._connect_tunnel(stream, addr, proxy_headers)
                        raise gen.Return(r)
                    else:
                        raise AttributeError('Unknown scheme: %s' % scheme)
                return _(addr)
            else:
                return stream.connect(addr)
        except socket.error as e:
            fu = Future()
            fu.set_exception(e)
            return fu

    @gen.coroutine
    def _connect_tunnel(self, sock, addr, headers):
        max_line = 65536
        yield sock.write(('CONNECT %s:%d HTTP/1.0\r\n' % addr).encode())
        for header, value in headers.items():
            yield sock.write(('%s: %s\r\n' % (header, value)).encode())
        yield sock.write(b'\r\n')

        # Initialize with Simple-Response defaults
        line = yield sock.read_until(b'\r\n', max_bytes=max_line)
        if not line:
            # Presumably, the server closed the connection before
            # sending a valid response.
            raise BadStatusLine(line)
        line = line.decode()
        try:
            [version, status, reason] = line.split(None, 2)
        except ValueError:
            try:
                [version, status] = line.split(None, 1)
                reason = ''
            except ValueError:
                # empty version will cause next test to fail and status
                # will be treated as 0.9 response.
                version = ''
        if not version.startswith('HTTP/'):
            version, status, reason = 'HTTP/0.9', 200, ''

        else:
            try:
                status = int(status)
                if status < 100 or status > 999:
                    raise BadStatusLine(line)
            except ValueError:
                raise BadStatusLine(line)

        if version == 'HTTP/0.9':
            # HTTP/0.9 doesn't support the CONNECT verb, so if httplib has
            # concluded HTTP/0.9 is being used something has gone wrong.
            sock.close()
            raise socket.error('Invalid response from tunnel request')
        if status != 200:
            sock.close()
            raise socket.error('Tunnel connection failed: %d %s' % (status,
                                                                    reason.strip()))
        while True:
            line = yield sock.read_until(b'\r\n', max_bytes=max_line)
            line = line.decode()
            if not line:
                # for sites which EOF without sending trailer
                break
            if line == '\r\n':
                break

    def _negotiate_socks(self, addr, proxy_addr):
        parsed = urlparse(proxy_addr[0])

        if parsed.scheme == 'socks5':
            socks_version, rdns = 2, False
        elif parsed.scheme == 'socks5h':
            socks_version, rdns = 2, True
        elif parsed.scheme == 'socks4':
            socks_version, rdns = 1, False
        elif parsed.scheme == 'socks4a':
            socks_version, rdns = 1, True
        else:
            raise ValueError(
                'Unable to determine SOCKS version from %s' % addr[0])
        username, password = get_auth_from_url(addr[0])
        stream = SockIOStream((
            socks_version, rdns, parsed.hostname, proxy_addr[1], username, password))
        return stream.connect(*addr)


class HTTPAdapter(BaseAdapter):
    """The built-in HTTP Adapter for BaseIOStream.

    Provides a general-case interface for trip sessions to contact HTTP urls
    by implementing the Transport Adapter interface. This class will
    usually be created by the :class:`Session <Session>` class under the
    covers.

    :param max_retries: The maximum number of retries each connection
        should attempt. Note, this applies only to failed DNS lookups, socket
        connections and connection timeouts, never to requests where data has
        made it to the server. By default, Requests does not retry failed
        connections.
        #TODO: If you need granular control over the conditions under
        which we retry a request, import urllib3's ``Retry`` class and pass
        that instead.

    Usage::

      >>> import trip
      >>> s = trip.Session()
      >>> a = trip.adapters.HTTPAdapter(hostname_mapping='/etc/hosts')
      >>> s.mount('http://', a)
    """

    def __init__(self, io_loop=None, max_clients=10,
            hostname_mapping=None,
            max_buffer_size=104857600,
            max_header_size=None, max_body_size=None):
        super(HTTPAdapter, self).__init__()

        self.max_clients = max_clients
        self.queue = collections.deque()
        self.active = {}
        self.waiting = {}
        self.max_buffer_size = max_buffer_size
        self.max_header_size = max_header_size
        self.max_body_size = max_body_size
        self.io_loop = io_loop or IOLoop.current()

        self.resolver = Resolver()
        if hostname_mapping is not None:
            self.resolver = OverrideResolver(resolver=self.resolver,
                mapping=hostname_mapping)

        self.tcp_client = TCPClient(resolver=self.resolver)

    def send(self, request, stream=False, timeout=None, verify=True,
             cert=None, proxies=None):
        """Sends Request object. Returns Response object.

        :param request: The :class:`PreparedRequest <PreparedRequest>` being sent.
        :param stream: (optional) Whether to stream the request content.
        :param timeout: (optional) How long to wait for the server to send
            data before giving up, as a float, or a :ref:`(connect timeout,
            read timeout) <timeouts>` tuple.
        :type timeout: float or tuple
        :param verify: (optional) Whether to verify SSL certificates.
        :param cert: (optional) Any user-provided SSL certificate to be trusted.
        :param proxies: (optional) The proxies dictionary to apply to the request.
        :rtype: trip.adapters.MessageDelegate
        """
        future = Future()
        def callback(response):
            if isinstance(response, Exception):
                future.set_exception(response)
            else:
                future.set_result(response)
        key = object()
        request = (request, stream, timeout, verify, cert, proxies)
        self.queue.append((key, request, callback))
        if not len(self.active) < self.max_clients:
            timeout_handle = self.io_loop.add_timeout(
                self.io_loop.time() + min(parse_timeout(timeout)),
                functools.partial(self._on_timeout, key, 'in request queue'))
        else:
            timeout_handle = None
        self.waiting[key] = (request, callback, timeout_handle)
        self._process_queue()
        if self.queue:
            gen_log.debug('max_clients limit reached, request queued. '
                          '%d active, %d queued requests.' % (
                              len(self.active), len(self.queue)))
        return future

    def _process_queue(self):
        with stack_context.NullContext():
            while self.queue and len(self.active) < self.max_clients:
                key, request, callback = self.queue.popleft()
                if key not in self.waiting:
                    continue
                self._remove_timeout(key)
                self.active[key] = (request, callback)
                release_callback = functools.partial(self._release_fetch, key)
                self._handle_request(request, release_callback, callback)

    def _handle_request(self, request, release_callback, final_callback):
        request, stream, timeout, verify, cert, proxies = request
        HTTPConnection(request, release_callback, final_callback, self.tcp_client,
            self.max_buffer_size, self.max_header_size, self.max_body_size
            ).send(stream, timeout, verify, cert, proxies)

    def _release_fetch(self, key):
        del self.active[key]
        self._process_queue()

    def _remove_timeout(self, key):
        if key in self.waiting:
            request, callback, timeout_handle = self.waiting[key]
            if timeout_handle is not None:
                self.io_loop.remove_timeout(timeout_handle)
            del self.waiting[key]

    def _on_timeout(self, key, info=None):
        """Timeout callback of request.

        Construct a timeout HTTPResponse when a timeout occurs.

        :arg object key: A simple object to mark the request.
        :info string key: More detailed timeout information.
        """
        request, callback, timeout_handle = self.waiting[key]
        self.queue.remove((key, request, callback))

        error_message = 'Timeout {0}'.format(info) if info else 'Timeout'
        self.io_loop.add_callback(callback, Timeout(599, err_message))
        del self.waiting[key]

    def close(self):
        """Cleans up adapter specific items."""
        self.resolver.close()
        self.tcp_client.close()


class HTTPConnection(object):
    """Non-blocking HTTP client with no external dependencies.

    One HTTPConnection sticks to one request. Use HTTP1Connection
    inside for HTTP1.1 protocol.
    """
    def __init__(self, request,
            release_callback, final_callback, 
            tcp_client, max_buffer_size, 
            max_header_size, max_body_size):
        self.io_loop = IOLoop.current()
        self.request = request
        self.release_callback = release_callback
        self.final_callback = final_callback
        self.max_buffer_size = max_buffer_size
        self.tcp_client = tcp_client
        self.max_header_size = max_header_size
        self.max_body_size = max_body_size
        self._timeout = None

    def send(self, stream=False, timeout=None, verify=True,
             cert=None, proxies=None):
        request = self.request
        connect_timeout, self.read_timeout = parse_timeout(timeout)
        self.stream_body = stream

        # set connect timeout
        with stack_context.ExceptionStackContext(self._handle_exception):
            if connect_timeout:
                self._timeout = self.io_loop.call_later(connect_timeout,
                    stack_context.wrap(functools.partial(
                        self._on_timeout, 'while connecting')))

            # set proxy related info
            proxy = select_proxy(request.url, proxies)
            self.headers = request.headers.copy()
            if proxy:
                proxy = prepend_scheme_if_needed(proxy, 'http')
                parsed = urlparse(proxy)
                scheme, host, port = parsed.scheme, proxy, parsed.port
                port = port or (443 if scheme == 'https' else 80)
                self.start_line = RequestStartLine(request.method, request.url, '')
                self.headers.update(get_proxy_headers(proxy))
            else:
                host, port = None, None
                self.start_line = request.start_line

            self.tcp_client.connect(
                request.host, request.port,
                af=request.af,
                ssl_options=self._get_ssl_options(request, verify, cert),
                max_buffer_size=self.max_buffer_size,
                source_ip=host, source_port=port,
                callback=self._on_connect)

    def _on_connect(self, s):
        self.stream = s
        if self.final_callback is None:
            s.close()
            return
        self._remove_timeout()

        s.set_nodelay(True)

        connection = HTTP1Connection(
            s,
            HTTP1ConnectionParameters(
                no_keep_alive=True,
                max_header_size=self.max_header_size,
                max_body_size=self.max_body_size,
                decompress=self.request.decompress))

        if self.read_timeout:
            self._timeout = self.io_loop.call_later(self.read_timeout,
                stack_context.wrap(functools.partial(
                    self._on_timeout, 'during request')))

        connection.write_headers(self.start_line, self.headers)
        if self.request.body is not None:
            connection.write(self.request.body) #TODO: partial sending
        connection.finish()

        resp = MessageDelegate(self.request, connection, self._run_callback, self.stream_body)
        connection.read_headers(resp, callback=functools.partial(
            self._on_headers_received, connection, resp))

    def _on_headers_received(self, connection, resp, status):
        def _finish_read(status=None):
            self._remove_timeout()
            resp.finish()
        if not self.stream_body and status:
            connection.read_body(resp, callback=_finish_read)
        else:
            _finish_read()

    def _get_ssl_options(self, req, verify, cert):
        if urlsplit(req.url).scheme == "https":
            # If we are using the defaults, don't construct a new SSLContext.
            if req.ssl_options is not None:
                return req.ssl_options
            # deal with verify & cert
            ssl_options = {}

            if verify:
                cert_loc = None

                # Allow self-specified cert location.
                if verify is not True:
                    cert_loc = verify

                if not cert_loc:
                    cert_loc = DEFAULT_CA_BUNDLE_PATH

                if not cert_loc or not os.path.exists(cert_loc):
                    raise IOError("Could not find a suitable TLS CA certificate bundle, "
                                  "invalid path: {0}".format(cert_loc))

                # you may change this to avoid server's certificate check
                ssl_options["cert_reqs"] = 2 # ssl.CERT_REQUIRED
                ssl_options["ca_certs"] = cert_loc

            if cert:
                if not isinstance(cert, basestring):
                    cert_file = cert[0]
                    key_file = cert[1]
                else:
                    cert_file = cert
                    key_file = None

                if cert_file and not os.path.exists(cert_file):
                    raise IOError("Could not find the TLS certificate file, "
                                  "invalid path: {0}".format(conn.cert_file))
                if key_file and not os.path.exists(key_file):
                    raise IOError("Could not find the TLS key file, "
                                  "invalid path: {0}".format(conn.key_file))

                if key_file is not None:
                    ssl_options["keyfile"] = key_file
                if cert_file is not None:
                    ssl_options["certfile"] = cert_file

            # SSL interoperability is tricky.  We want to disable
            # SSLv2 for security reasons; it wasn't disabled by default
            # until openssl 1.0.  The best way to do this is to use
            # the SSL_OP_NO_SSLv2, but that wasn't exposed to python
            # until 3.2.  Python 2.7 adds the ciphers argument, which
            # can also be used to disable SSLv2.  As a last resort
            # on python 2.6, we set ssl_version to TLSv1.  This is
            # more narrow than we'd like since it also breaks
            # compatibility with servers configured for SSLv3 only,
            # but nearly all servers support both SSLv3 and TLSv1:
            # http://blog.ivanristic.com/2011/09/ssl-survey-protocol-support.html
            if (2, 7) <= sys.version_info:
                # In addition to disabling SSLv2, we also exclude certain
                # classes of insecure ciphers.
                ssl_options["ciphers"] = "DEFAULT:!SSLv2:!EXPORT:!DES"
            else:
                # This is really only necessary for pre-1.0 versions
                # of openssl, but python 2.6 doesn't expose version
                # information.
                ssl_options["ssl_version"] = 3 # ssl.PROTOCOL_TLSv1
            return ssl_options
        return None

    def _on_timeout(self, info=None):
        """Timeout callback of _HTTPConnection instance.

        Raise a timeout HTTPError when a timeout occurs.

        :info string key: More detailed timeout information.
        """
        self._timeout = None
        error_message = 'Timeout {0}'.format(info) if info else 'Timeout'
        if self.final_callback is not None:
            raise Timeout(599, error_message)

    def _remove_timeout(self, *args, **kwargs):
        if self._timeout is not None:
            self.io_loop.remove_timeout(self._timeout)
            self._timeout = None
    
    def _release(self):
        if self.release_callback is not None:
            release_callback = self.release_callback
            self.release_callback = None
            release_callback()

    def _run_callback(self, response):
        self._release()
        if self.final_callback is not None:
            final_callback = self.final_callback
            self.final_callback = None
            self.io_loop.add_callback(final_callback, response)

    def _handle_exception(self, type_, value, tb):
        if self.final_callback:
            self._remove_timeout()
            if isinstance(value, StreamClosedError):
                if value.real_error is None:
                    value = HTTPError(599, 'Stream closed')
                else:
                    value = value.real_error
                m = MessageDelegate(self.request, None, None)
                m.code, m.reason = 599, value
            else:
                m = value

            self._run_callback(m)

            if hasattr(self, 'stream'):
                self.stream.close()
            return True
        else:
            return isinstance(value, StreamClosedError)


class HTTP1Connection(_HTTP1Connection):
    """Implements the HTTP/1.x protocol.
    """

    def __init__(self, stream, params=None):
        _HTTP1Connection.__init__(self, stream, True, params)

    def _parse_delegate(self, delegate):
        if not hasattr(delegate, '_delegate'):
            if self.params.decompress:
                delegate._delegate = GzipMessageDelegate(delegate, self.params.chunk_size)
            else:
                delegate._delegate = None
        return delegate, delegate._delegate or delegate

    @gen.coroutine
    def read_headers(self, delegate):
        try:
            _delegate, delegate = self._parse_delegate(delegate)
            header_future = self.stream.read_until_regex(
                b"\r?\n\r?\n",
                max_bytes=self.params.max_header_size)
            header_data = yield header_future
            start_line, headers = self._parse_headers(header_data)

            start_line = parse_response_start_line(start_line)
            self._response_start_line = start_line

            self._disconnect_on_finish = not self._can_keep_alive(
                start_line, headers)

            with _ExceptionLoggingContext(app_log):
                header_future = delegate.headers_received(start_line, headers)
                if header_future is not None:
                    yield header_future
            if self.stream is None:
                # We've been detached.
                raise gen.Return(False)

            # determine body skip
            #TODO: 100 <= code < 200
            if (self._request_start_line is not None and
                    self._request_start_line.method == 'HEAD'):
                _delegate.skip_body = True
            code = start_line.code
            if code == 304:
                # 304 responses may include the content-length header
                # but do not actually have a body.
                # http://tools.ietf.org/html/rfc7230#section-3.3
                _delegate.skip_body = True
            if code >= 100 and code < 200:
                # 1xx responses should never indicate the presence of
                # a body.
                if ('Content-Length' in headers or
                        'Transfer-Encoding' in headers):
                    raise HTTPInputError(
                        "Response code %d cannot have body" % code)
                # TODO: client delegates will get headers_received twice
                # in the case of a 100-continue.  Document or change?
                yield self.read_headers(delegate)
        except HTTPInputError as e:
            gen_log.info("Malformed HTTP message from %s: %s",
                         self.context, e)
            self.close()

            self._clear_callbacks()

            raise gen.Return(False)
        finally:
            header_future = None
        raise gen.Return(True)

    @gen.coroutine
    def read_body(self, delegate):
        _delegate, delegate = self._parse_delegate(delegate)
        need_delegate_close = True

        if not _delegate.skip_body:
            try:
                body_future = self._read_body(
                    _delegate.code, _delegate.headers, delegate)
                if body_future is not None:
                    yield body_future

                self._read_finished = True
                need_delegate_close = False

                # If we're waiting for the application to produce an asynchronous
                # response, and we're not detached, register a close callback
                # on the stream (we didn't need one while we were reading)
                if (not self._finish_future.done() and
                        self.stream is not None and
                        not self.stream.closed()):
                    self.stream.set_close_callback(self._on_connection_close)
                    yield self._finish_future
                if self._disconnect_on_finish:
                    self.close()
                if self.stream is None:
                    raise gen.Return(False)
            except HTTPInputError as e:
                gen_log.info("Malformed HTTP message from %s: %s",
                             self.context, e)
                self.close()
                raise gen.Return(False)
            finally:
                if need_delegate_close:
                    with _ExceptionLoggingContext(app_log):
                        delegate.on_connection_close(self.stream.error)
                self._clear_callbacks()
        raise gen.Return(True)

    @gen.coroutine
    def read_stream_body(self, delegate, chunk_size=1, stream_callback=None):
        _delegate, delegate = self._parse_delegate(delegate)
        remain_content = False
        need_delegate_close = True

        if not _delegate.skip_body:
            try:
                body_future = self._read_stream_body(chunk_size, delegate)
                if body_future is not None:
                    remain_content = yield body_future
                need_delegate_close = False

                if not remain_content:
                    self._read_finished = True
                    if (not self._finish_future.done() and
                            self.stream is not None and
                            not self.stream.closed()):
                        self.stream.set_close_callback(self._on_connection_close)
                        yield self._finish_future
                    if self._disconnect_on_finish:
                        self.close()
            except HTTPInputError as e:
                gen_log.info("Malformed HTTP message from %s: %s",
                             self.context, e)
                self.close()
                remain_content = False
            finally:
                if need_delegate_close:
                    with _ExceptionLoggingContext(app_log):
                        delegate.on_connection_close(self.stream.error)
                if not remain_content:
                    self._clear_callbacks()
        raise gen.Return(remain_content)

    @gen.coroutine
    def _read_stream_body(self, content_length, delegate):
        while 0 < content_length:
            try:
                body = yield self.stream.read_bytes(
                    min(self.params.chunk_size, content_length), partial=True)
            except StreamClosedError:
                # with partial stream will update close status after receiving
                # the last chunk, so we catch StreamClosedError instead
                raise gen.Return(False)
            content_length -= len(body)
            if not self._write_finished or self.is_client:
                with _ExceptionLoggingContext(app_log):
                    ret = delegate.data_received(body)
                    if ret is not None:
                        yield ret
        raise gen.Return(True)


class MessageDelegate(HTTPMessageDelegate):
    """ Message delegate.
    """

    def __init__(self, request, connection,
            final_callback, stream=False):
        self.code = None
        self.reason = None
        self.headers = None
        self.body = None
        self.chunks = []

        self.request = request
        self.connection = connection
        self.final_callback = final_callback
        self.stream = stream

        self.io_loop = IOLoop.current()

        self.skip_body = False

    def headers_received(self, start_line, headers):
        """Called when the HTTP headers have been received and parsed.

        :arg start_line: a `.RequestStartLine` or `.ResponseStartLine`
            depending on whether this is a client or server message.
        :arg headers: a `.HTTPHeaders` instance.

        Some `.HTTPConnection` methods can only be called during
        ``headers_received``.

        May return a `.Future`; if it does the body will not be read
        until it is done.
        """
        self.code = start_line.code
        self.reason = start_line.reason
        self.headers = headers

    def data_received(self, chunk):
        """Called when a chunk of data has been received.

        May return a `.Future` for flow control.
        """
        if self.body:
            self.body.write(chunk)
        else:
            self.chunks.append(chunk)

    def finish(self):
        """Called after the last chunk of data has been received."""
        data = b''.join(self.chunks)
        if self.stream:
            buffer_ = BytesIO()
        else:
            buffer_ = BytesIO(data)
        self.body = buffer_
        self._run_callback(self)

    def on_connection_close(self, error=None):
        """Called if the connection is closed without finishing the request.

        If ``headers_received`` is called, either ``finish`` or
        ``on_connection_close`` will be called, but not both.
        """
        error = error or HTTPError(599, 'Connection closed')
        self.reason = (self.reason, self.code, error)
        self.code = 599
        self._run_callback(self)

    def _run_callback(self, response):
        if self.final_callback is not None:
            final_callback = self.final_callback
            self.final_callback = None
            self.io_loop.add_callback(final_callback, response)


class GzipMessageDelegate(_GzipMessageDelegate):
    """Wraps an `HTTPMessageDelegate` to decode ``Content-Encoding: gzip``.
    rewrite to avoid circle reference
    """
    @property
    def _delegate(self):
        return self._delegate_ref()

    @_delegate.setter
    def _delegate(self, value):
        self._delegate_ref = ref(value)

    def on_connection_close(self, error=None):
        if self._delegate:
            return self._delegate.on_connection_close(error)
