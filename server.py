#!/usr/bin/python
# VERSION 0.1

import os
import getopt
import signal
import time
from sys import argv, exit
from struct import pack, unpack

from SelectServer import SelectServer

class ClientConnection(SelectServer.BaseHandlerClass):
    """
    Each client connection is represented by an object of this class.
    When connected, the setup function is run, followed by handle().
    """

    def setup(self, args):
        self.commands = {
            "GET" : self.get,
            "bye" : self.bye
        }
        self.CHUNKSIZE = 1024
        signal.signal(signal.SIGALRM, self.alarm_handler)

    def handle(self, args):

        signal.alarm(5) # set a 5-second timeout
        #print "got connection from " + str(self.client_address[0])
        data = ""
        while "\n" not in data:
            ret = self.recv(1024)
            if not ret:
                signal.alarm(0) # disable the timeout
                self.update_stats('error_msgs', "[" + ' '.join(data) + "] " +
                "hung up before command could be received", SelectServer.SelectServer.STATS_APPEND)
                return
            data += ret
        signal.alarm(0) # disable the timeout

        data = data.strip()
        #print str(data)
        self.update_stats('commands_executed', str(data), SelectServer.SelectServer.STATS_APPEND)

        data = data.split(" ")
        if data[0] in self.commands:
            ret_msg = self.commands[data[0]](data[1:])
        else:
            ret_msg = "command '" + data[0] + "' not recognized\n"
            self.sendall(ret_msg)
        self.update_stats('error_msgs', "[" + ' '.join(data) + "] " + ret_msg, SelectServer.SelectServer.STATS_APPEND)

    def finish(self, args):
        #print str(self.client_address[0]) + " hung up"
        pass

    def get(self, args):
        if len(args) == 0:
            return "Not enough arguments"
        fylker = map(int, args)

        #print str(self.client_address[0]) + " in get(): " + str(fylker)

        # if client asked for more than one fylke
        if len(fylker) > 1:
            return self.__get_many(fylker)

        # if client asked for only one fylke
        try:
            infile = open("./fylkedata/fylke_" + str(fylker[0]) + ".kdtree.bin", "r")
        except IOError as e:
            error = "I/O error({0}): {1}\n".format(e.errno, e.strerror)
            self.sendall(error)
            return error
        filesize = os.fstat(infile.fileno()).st_size

        self.sendall(pack("<i", filesize))

        for i in xrange(0, filesize, self.CHUNKSIZE):
            self.sendall(infile.read(self.CHUNKSIZE))
        infile.close()

        return "Success"

    def __get_many(self, fylker):
        readpipe, writepipe = os.pipe()

        if not os.fork():
            os.close(readpipe)

            args = ["parsecoords", "-d",  str(writepipe)] + map(str, fylker)
            os.execv("./createBinaryFile/parsecoords", args)
            os._exit(1) # only happens on error

        os.close(writepipe)

        size = os.read(readpipe, 4)
        self.sendall(size)

        size = unpack("<i", size)[0]
        #print "size: %d" % size
        for i in xrange(0, size, self.CHUNKSIZE):
            self.sendall(os.read(readpipe, self.CHUNKSIZE))
        os.close(readpipe)

        os.wait() # we don't want any zombies

        return "Success"

    def bye(self, args):
        self.sendall("byebye")

    def alarm_handler(self, signum, frame):
        print "timeout on %s" % self.client_address[0]
        exit(1)

def daemon():
    if not os.fork():
        os.setsid()
        if os.fork():
            os._exit(0)
        #os.chdir("/")
        os.umask(0)

        devnull = os.open("/dev/null", os.O_RDWR)
        os.dup2(devnull, 0)
        os.dup2(devnull, 1)
        os.dup2(devnull, 2)
        os.close(devnull)
    else:
        os._exit(0)


daemonize = False
HOST, PORT = "", 1234

try:
    opts, args = getopt.getopt(argv[1:], "p:d", ["port=", "damonize"])
except getopt.GetoptError as err:
    # print help information and exit:
    print str(err) # will print something like "option -a not recognized"
    os._exit(1)
output = None
verbose = False
for o, a in opts:
    if o == "-d":
        daemonize = True
    elif o in ("-p", "--port"):
        PORT = int(a)
    else:
        assert False, "unhandled option"

if daemonize:
    daemon()

server = SelectServer.SelectServer(HOST, PORT, ClientConnection)
server.start()
