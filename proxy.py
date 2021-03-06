# -*- coding: utf-8 -*-
#!/usr/bin/env python
'''
owtf is an OWASP+PTES-focused try to unite great tools & facilitate pentesting
Copyright (c) 2013, Abraham Aranguren <name.surname@gmail.com>  http://7-a.org
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the copyright owner nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Inbound Proxy Module developed by Bharadwaj Machiraju (blog.tunnelshade.in)
#                     as a part of Google Summer of Code 2013

# Modified by md5_salt (5alt.me)
'''
import tornado.httpserver
import tornado.ioloop
import tornado.iostream
import tornado.gen
import tornado.web
import tornado.curl_httpclient
import socket
import ssl
import tornado.escape
import tornado.httputil
import os
import re
import json
from collections import defaultdict

from socket_wrapper import wrap_socket

from sqlalchemy import *
from sqlalchemy.exc import *

import HTMLParser
html_parser = HTMLParser.HTMLParser()


# TODO: 重新设计数据库
class IndexDB(object):
    def __init__(self):
        engine = create_engine('sqlite:///data.db', encoding='utf-8', echo=False)
        metadata = MetaData(engine)
        try:
            self.table = Table('index', metadata, autoload=True)
        except NoSuchTableError:
            self.table = Table('index', metadata,
                               Column('id', Integer, primary_key=True, nullable=False, autoincrement=True),
                               Column('nickname', String(32)),
                               Column('title', String(64)),
                               Column('url', String(512)),
                               )
            self.table.create()
            Index('idx_nickname_title', self.table.c.nickname, self.table.c.title)  # 联合索引

    def insert_or_update(self, nickname, title, url):
        rs = self.table.select().where(and_(self.table.c.nickname == nickname, self.table.c.title == title)).execute()
        if not rs.fetchone():
            self.table.insert().values(nickname=nickname, title=title, url=url).execute()

    def filter(self, nickname):
        rs = self.table.select().where(self.table.c.nickname == nickname).order_by(desc('id')).execute()
        res = rs.fetchall()[:10]
        return res


# index_db = IndexDB()


class WebHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ['GET']

    @tornado.gen.coroutine
    def get(self, data):
        self.write('Hello World!')


class ProxyHandler(tornado.web.RequestHandler):
    """
    This RequestHandler processes all the requests that the application recieves
    """
    SUPPORTED_METHODS = ['GET', 'POST', 'CONNECT', 'HEAD', 'PUT', 'DELETE', 'OPTIONS', 'PATCH']

    cakey = 'ca.key'
    cacert = 'ca.crt'
    certdir = 'certs/'

    response_body = None

    def request_handler(self, request):
        pass

    def response_handler(self, request, response, response_body):
        if self.request.host in self.request.uri.split('/') or self.request.uri.startswith('http://'):
            url = self.request.uri
        else:
            url = self.request.protocol + "://" + self.request.host + self.request.uri
        # TODO: 减少业务逻辑
        if re.match(r'http://[a-z]{2}\.snssdk\.com/api/news/feed/v86/', url, re.S):
            res = json.loads(response_body)
            if res.get("message") == "success":
                for d in res["data"]:
                    content = json.loads(d["content"])
                    if 'article_url' in content:
                        index = content['article_url']
                        print index

    def save_handler(self, request, response, response_body):
        pass

    def set_status(self, status_code, reason=None):
        """Sets the status code for our response.
        Overriding is done so as to handle unknown
        response codes gracefully.
        """
        self._status_code = status_code
        if reason is not None:
            self._reason = tornado.escape.native_str(reason)
        else:
            try:
                self._reason = tornado.httputil.responses[status_code]
            except KeyError:
                self._reason = tornado.escape.native_str("Unknown Error")

    @tornado.gen.coroutine
    def get(self):
        """
        * This function handles all requests except the connect request.
        * Once ssl stream is formed between browser and proxy, the requests are
          then processed by this function
        """
        if self.request.uri == '/favicon.ico':  # 针对浏览器
            return

        # Data for handling headers through a streaming callback
        restricted_headers = ['Content-Length',
                            'Content-Encoding',
                            'Etag',
                            'Transfer-Encoding',
                            'Connection',
                            'Vary',
                            'Accept-Ranges',
                            'Pragma']

        # This function is a callback after the async client gets the full response
        # This method will be improvised with more headers from original responses
        def handle_response(response):
            self.response_body = response.body if response.body else self.response_body

            # Hook response
            ret = self.response_handler(self.request, response, self.response_body)
            if ret:
                self.response_body = ret
            if self.response_body:
                self.write(self.response_body)

            self.set_status(response.code)
            for header, value in list(response.headers.items()):
                if header == "Set-Cookie":
                    self.add_header(header, value)
                else:
                    if header not in restricted_headers:
                        self.set_header(header, value)

            # self.set_header('Content-Type', response.headers['Content-Type'])
            self.finish()

            # Save request and response
            self.save_handler(self.request, response, self.response_body)

        # This function is a callback when a small chunk is recieved
        def handle_data_chunk(data):
            if data:
                if not self.response_body:
                    self.response_body = data
                else:
                    self.response_body += data

        # Hook request
        self.request_handler(self.request)

        # The requests that come through ssl streams are relative requests, so transparent
        # proxying is required. The following snippet decides the url that should be passed
        # to the async client
        if self.request.host in self.request.uri.split('/') or self.request.uri.startswith('http://'):  # Normal Proxy Request
            url = self.request.uri
        else:  # Transparent Proxy Request
            url = self.request.protocol + "://" + self.request.host + self.request.uri

        # More headers are to be removed
        for header in ('Connection', 'Pragma', 'Cache-Control'):
            try:
                del self.request.headers[header]
            except:
                continue

        # httprequest object is created and then passed to async client with a callback
        # pycurl is needed for curl client

        async_client = tornado.curl_httpclient.CurlAsyncHTTPClient()
        # TODO: gzip问题
        request = tornado.httpclient.HTTPRequest(
                url=url,
                method=self.request.method,
                body=self.request.body if self.request.method != 'GET' else None,
                headers=self.request.headers,
                follow_redirects=False,
                use_gzip=True,
                streaming_callback=handle_data_chunk,
                header_callback=None,
                proxy_host=self.application.outbound_ip,
                proxy_port=self.application.outbound_port,
                allow_nonstandard_methods=True,
                validate_cert=False)

        try:
            yield async_client.fetch(request, callback=handle_response)
        except Exception as e:
            print e

    # The following 5 methods can be handled through the above implementation
    @tornado.gen.coroutine
    def post(self):
        yield self.get()

    @tornado.gen.coroutine
    def head(self):
        yield self.get()

    @tornado.gen.coroutine
    def put(self):
        yield self.get()

    @tornado.gen.coroutine
    def delete(self):
        yield self.get()

    @tornado.gen.coroutine
    def options(self):
        yield self.get()

    @tornado.gen.coroutine
    def connect(self):
        # if os.path.isfile(self.cakey) and os.path.isfile(self.cacert) and os.path.isdir(self.certdir):
        if re.match(r"mp\.weixin\.qq\.com:443|(?!ib)[a-z]{2}\.snssdk\.com:443", self.request.host):
            self.connect_intercept()
        else:
            self.connect_relay()

    def connect_intercept(self):
        """
        This function gets called when a connect request is recieved.
        * The host and port are obtained from the request uri
        * A socket is created, wrapped in ssl and then added to SSLIOStream
        * This stream is used to connect to speak to the remote host on given port
        * If the server speaks ssl on that port, callback start_tunnel is called
        * An OK response is written back to client
        * The client side socket is wrapped in ssl
        * If the wrapping is successful, a new SSLIOStream is made using that socket
        * The stream is added back to the server for monitoring
        """
        host, port = self.request.uri.split(':')

        def start_tunnel():
            try:
                self.request.connection.stream.write(b"HTTP/1.1 200 OK CONNECTION ESTABLISHED\r\n\r\n")
                wrap_socket(self.request.connection.stream.socket, host, success=ssl_success)
            except tornado.iostream.StreamClosedError:
                pass

        def ssl_success(client_socket):
            client = tornado.iostream.SSLIOStream(client_socket)
            server.handle_stream(client, self.application.inbound_ip)  # lint:ok

        try:
            s = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0))
            upstream = tornado.iostream.SSLIOStream(s)
            yield upstream.connect((host, int(port)), start_tunnel, host)
        except Exception:
            print "[!] Dropping CONNECT request to " + self.request.uri
            self.write(b"404 Not Found :P")
            self.finish()

    def connect_relay(self):
        host, port = self.request.uri.split(':')
        client = self.request.connection.stream

        def read_from_client(data):
            upstream.write(data)

        def read_from_upstream(data):
            client.write(data)

        def client_close(data=None):
            if upstream.closed():
                return
            if data:
                upstream.write(data)
            upstream.close()

        def upstream_close(data=None):
            if client.closed():
                return
            if data:
                client.write(data)
            client.close()

        def start_tunnel():
            client.read_until_close(client_close, read_from_client)
            upstream.read_until_close(upstream_close, read_from_upstream)
            client.write(b'HTTP/1.0 200 Connection established\r\n\r\n')

        def on_proxy_response(data=None):
            if data:
                first_line = data.splitlines()[0]
                http_v, status, text = first_line.split(None, 2)
                if int(status) == 200:
                    start_tunnel()
                    return

            self.set_status(500)
            self.finish()

        def start_proxy_tunnel():
            upstream.write('CONNECT %s HTTP/1.1\r\n' % self.request.uri)
            upstream.write('Host: %s\r\n' % self.request.uri)
            upstream.write('Proxy-Connection: Keep-Alive\r\n\r\n')
            upstream.read_until('\r\n\r\n', on_proxy_response)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        upstream = tornado.iostream.IOStream(s)

        if self.application.outbound_ip and self.application.outbound_port:
            yield upstream.connect((self.application.outbound_ip, self.application.outbound_port), start_proxy_tunnel)
        else:
            yield upstream.connect((host, int(port)), start_tunnel)


class ProxyServer(object):
    def __init__(self, handler, inbound_ip="0.0.0.0", inbound_port=8888, outbound_ip=None, outbound_port=None):
        self.application = tornado.web.Application(handlers=[
            (r"^/geturls/(\w*)", WebHandler),
            (r".*", ProxyHandler),
        ], debug=False, gzip=True)
        self.application.inbound_ip = inbound_ip
        self.application.inbound_port = inbound_port
        self.application.outbound_ip = outbound_ip
        self.application.outbound_port = outbound_port
        global server
        server = tornado.httpserver.HTTPServer(self.application, decompress_request=True)
        self.server = server

    # "0" equals the number of cores present in a machine
    def start(self, instances=0):
        try:
            # total = Profiler()
            # app = tornado.web.Application(handlers=[(r".*", handler)], debug=False, gzip=True)
            # global http_server  # Easy to add SSLIOStream later in the request handlers
            # http_server = tornado.httpserver.HTTPServer(app)
            self.server.bind(self.application.inbound_port, address=self.application.inbound_ip)

            # To run any number of instances
            self.server.start(instances)
            tornado.ioloop.IOLoop.instance().start()

        except Exception as e:
            print(e)

    def stop(self):
        tornado.ioloop.IOLoop.instance().stop()
        print("[!] Shutting down the proxy server")


if __name__ == "__main__":
    try:
        proxy = ProxyServer(ProxyHandler)
        proxy.start()
    except KeyboardInterrupt:
        proxy.stop()
