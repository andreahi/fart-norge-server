#!/usr/bin/python
# VERSION 0.1

import SocketServer
import os
import signal
from sys import argv
from struct import pack, unpack

class ClientConnection(SocketServer.BaseRequestHandler):
    """
    Each client connection is represented by an object of this class.
    When connected, the setup function is run, followed by handle().
    """

    def setup(self):
        self.commands = {
            "GET" : self.get,
            "bye" : self.bye
        }
        self.CHUNKSIZE = 1024
        signal.signal(signal.SIGALRM, self.alarm_handler)

    def handle(self):

        signal.alarm(5) # set a 5-second timeout
        print "got connection from " + str(self.client_address[0])
        data = ""
        while "\n" not in data:
            data = data + self.request.recv(1024)
        signal.alarm(0) # disable the timeout

        data = data.strip().split(" ")

        if data[0] in self.commands:
            self.commands[data[0]](data[1:])
        else:
            self.request.sendall("command '" + data[0] + "' not recognized\n")

    def finish(self):
        print str(self.client_address[0]) + " hung up"

    def get(self, args):
        if len(args) == 0:
            return
        fylker = map(int, args)

        print str(self.client_address[0]) + " in get(): " + str(fylker)

        # if client asked for more than one fylke
        if len(fylker) > 1:
            self.__get_many(fylker)
            return

        # if client asked for only one fylke
        try:
            infile = open("./fylkedata/fylke_" + str(fylker[0]) + ".kdtree.bin", "r")
        except IOError as e:
            self.request.sendall("I/O error({0}): {1}\n".format(e.errno, e.strerror))
            return
        filesize = os.fstat(infile.fileno()).st_size

        self.request.sendall(pack("<i", filesize))

        for i in xrange(0, filesize, self.CHUNKSIZE):
            self.request.sendall(infile.read(self.CHUNKSIZE))
        infile.close()

    def __get_many(self, fylker):
        readpipe, writepipe = os.pipe()

        if not os.fork():
            os.close(readpipe)

            args = ["parsecoords", "-d",  str(writepipe)] + map(str, fylker)
            os.execv("./createBinaryFile/parsecoords", args)
            os._exit(1) # only happens on error

        os.close(writepipe)

        size = os.read(readpipe, 4)
        self.request.sendall(size)

        size = unpack("<i", size)[0]
        print "size: %d" % size
        for i in xrange(0, size, self.CHUNKSIZE):
            self.request.sendall(os.read(readpipe, self.CHUNKSIZE))
        os.close(readpipe)

        os.wait() # we don't want any zombies

    def bye(self, args):
        self.request.sendall("byebye")

    def alarm_handler(self, signum, frame):
        print "timeout on %s" % self.client_address[0]
        os._exit(1)


class TCPServer(SocketServer.TCPServer):
    allow_reuse_address = True

class TCPForkServer(SocketServer.ForkingMixIn, TCPServer):
    pass


HOST, PORT = "", 1234
if len(argv) > 1:
    PORT = int(argv[1])

server = TCPForkServer((HOST, PORT), ClientConnection)
server.serve_forever()
