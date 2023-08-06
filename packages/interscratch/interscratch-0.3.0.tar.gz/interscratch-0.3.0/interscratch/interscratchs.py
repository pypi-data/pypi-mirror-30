#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import socket
import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.options

from tornado.options import define, options

define("port", default=3000, help="run on the given port", type=int)

def get_hostname():
    return socket.gethostname()

def get_ip():
    return (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [
        [(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in
         [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]

class Application(tornado.web.Application):
    def __init__(self):
        client_list = set()
        handlers = [(r"/", MainHandler, dict(client_list=client_list))]
        settings = dict(debug=True)
        tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.websocket.WebSocketHandler):
    def initialize(self, client_list):
        self.clients = client_list

    def check_origin(self, origin):
        return True

    def open(self):
        logging.info("A client connected.")
        self.clients.add(self)

    def on_close(self):
        logging.info("A client disconnected")

    def on_message(self, message):
        logging.info("message: {}".format(message))
        for a_client in self.clients:
            a_client.write_message(message)

def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    print "To connect a client, use:"
    print "interscratchc --server=%s"%get_ip()
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()