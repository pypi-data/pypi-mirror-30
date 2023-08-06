import argparse
import logging
import sys

import tornado.ioloop
import tornado.web
import Queue

from tornado.ioloop import IOLoop
from tornado import gen
from tornado.websocket import websocket_connect
import tornado.queues


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARN)

read_request_queue = Queue.Queue()
send_message_queue = tornado.queues.Queue()
read_message_queue = tornado.queues.Queue()

SCRATCH_MESSAGE = "lastMessage"
PORT = 8000


class WSClient(object):
    def __init__(self, url, timeout, read_msg_queue, send_msg_queue):
        self.url = url
        self.timeout = timeout
        self.read_msg_queue = read_msg_queue
        self.send_msg_queue = send_msg_queue
        self.ioloop = IOLoop.instance()
        self.ws = None
        self.connect()
        self.ioloop.call_later(1, self.send)


    @gen.coroutine
    def connect(self):
        logger.warn("trying to connect to %s", self.url)
        try:
            self.ws = yield websocket_connect(self.url)
        except Exception as e:
            logger.warn("connection error : %s"%e.message)
        else:
            logger.warn("connected")
            self.run()

    @gen.coroutine
    def run(self):
        while True:
            msg = yield self.ws.read_message()
            logger.warn("Received, " + msg)
            if msg is None:
                logger.warn("connection closed")
                self.ws = None
                break
            self.read_msg_queue.put_nowait(msg)

    @gen.coroutine
    def send(self):
        while True:
            message = yield self.send_msg_queue.get()
            self.ws.write_message(message)

def run_ws_client(url, timeout, read_msg_queue, send_msg_queue):
    WSClient(url, timeout, read_msg_queue, send_message_queue)

class PollHandler(tornado.web.RequestHandler):
    def initialize(self):
        pass

    def get(self):
        if (not read_message_queue.empty()) and (not read_request_queue.empty()):
            msg = read_message_queue.get_nowait()
            _id = read_request_queue.get_nowait()
            logger.warn("Poll:%s" % msg)
            self.write("%s %s"%(SCRATCH_MESSAGE, msg))

        # wait signaling
        if read_request_queue.empty():
            return
        d = read_request_queue.queue
        self.write("_busy")
        for id in d:
            self.write(" %i" % id)


class SendHandler(tornado.web.RequestHandler):
    def get(self, message):
        logger.warn("Send:%s"%message)
        send_message_queue.put_nowait(message)


class ReadHandler(tornado.web.RequestHandler):
    def get(self, id):
        logger.warn("Read, id:%i"%int(id))
        read_request_queue.put_nowait(int(id))


class ResetHandler(tornado.web.RequestHandler):
    def get(self):
        logger.warn("Reset all")
        global read_message_queue, read_request_queue, send_message_queue

        while not read_request_queue.empty():
            read_request_queue.get_nowait()
        while not send_message_queue.empty():
            send_message_queue.get_nowait()
        while not read_message_queue.empty():
            read_message_queue.get_nowait()

def make_app(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', '-s', default='localhost', help='specify interscratch server')
    args = parser.parse_args()
    ws_client_url = "ws://%s:3000" % args.server
    run_ws_client(ws_client_url, 5, read_message_queue, send_message_queue)

    return tornado.web.Application([
        (r"/poll", PollHandler),
        (r"/send/(.*)", SendHandler),
        (r"/read/(.*)", ReadHandler),
        (r"/reset_all", ResetHandler),
    ])

def main():
    app = make_app(sys.argv)
    app.listen(PORT)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
