#!/usr/bin/python

import socket
import select
import thread
import threading
import os
import time
import json

from multiprocessing import Queue

class SelectServer:

    def __init__(self, host, port, handler_class, max_conn=100, args=None): # {
        self.sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sd.bind((host, port))
        self.sd.listen(max_conn)

        self.args = args
        self.handler_class = handler_class

        self.stats = {"open_conns": 0}
        self.stats_lock = threading.RLock()
    # }

    def read_stats(self, key): # {
        ret = ""

        self.stats_lock.acquire()
        if key == '*':
            ret = self.stats
        elif key in self.stats:
            ret = self.stats[key]
        self.stats_lock.release()

        return ret
    # }

    def client_connection(self, session_id, cl_addr, request, queue): # {
        self.stats = None

        handler = self.handler_class(session_id, cl_addr, request, queue)

        handler.setup(self.args)
        handler.handle(self.args)
        handler.finish(self.args)

        #queue.put((cl_addr[0], session_id, 'time_disconnected', time.time(), self.STATS_SET))

    # }

    def start_console(self, request, client_address): # {
        commands = [
            'get_commands',
            'open_conns',
            'all_stats',
            'bye',
        ]
        while True:
            data = request.recv(1024)

            if data == '': 
                break

            data = data.strip()
            if data == '':
                continue

            data = data.split()
            if data[0] == 'get_commands':
                request.sendall(json.dumps(commands))
            elif data[0] == 'open_conns':
                request.sendall(json.dumps(self.read_stats('open_conns')))
            elif data[0] == 'all_stats':
                request.sendall(json.dumps(self.read_stats('*')))
            elif data[0] == 'bye':
                break
            else:
                request.sendall(json.dumps("No such command"))

        request.close()
        thread.exit()
   # }

    STATS_ADD = 1
    STATS_SET = 2
    STATS_APPEND = 3
    def update_stats(self, addr, session_id, key, value, flag=STATS_ADD): # {
        self.stats_lock.acquire()
        if not addr and not session_id:
            self.stats[key] = value
            self.stats_lock.release()
            return

        # make sure the addr and session_id dictionaries exists
        if addr not in self.stats:
            self.stats[addr] = {}
        if session_id not in self.stats[addr]:
            self.stats[addr][session_id] = {}

        #print "key: %s, flag: %d" % (key, flag)

        # the key '*' is used for registering a new session
        if key != '*':
            if self.STATS_ADD == flag:
                self.stats[addr][session_id][key] += value
            elif self.STATS_SET == flag:
                self.stats[addr][session_id][key] = value
                if key == 'time_disconnected':
                    self.stats['open_conns'] = self.stats['open_conns'] - 1
            elif self.STATS_APPEND == flag:
                self.stats[addr][session_id][key].append(value)
        else:
            self.stats[addr][session_id] = value
        self.stats_lock.release()
    # }

    def recv_stats(self, queue): # {
        while True:
            cl_addr, session_id, key, value, flag = queue.get()
            self.update_stats(cl_addr, session_id, key, value, flag)
    # }

    def start(self): # {
        consolesd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        consolesd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        consolesd.bind(("localhost", 1233))
        consolesd.listen(2)

        infds = [self.sd, consolesd]
        curr_sid = 0 # next new session id
        queue = Queue()

        thread.start_new_thread(self.recv_stats, (queue,))

        while True:
            rlist, wlist, xlist = select.select(infds, [], [])

            for s in rlist:
                if s == self.sd:
                    # print json.dumps(self.stats, indent=4)
                    # fork and create client object
                    request, client_address = s.accept()

                    if not os.fork():
                        s.close()
                        self.client_connection(curr_sid, client_address, request, queue)

                        os._exit(1)

                    stats = {
                        'time_connected': time.time(), # at what time did the client connect
                        'time_disconnected': None, # at what time did the client connect
                        'bytes_received': 0,
                        'bytes_sent': 0,
                        'commands_executed': [],
                        'error_msgs': [],
                    }
                    self.update_stats(client_address[0], curr_sid, '*', stats)

                    request.close()

                    self.update_stats(None, None, "open_conns", self.read_stats("open_conns") + 1)
                    curr_sid = curr_sid + 1

                elif s == consolesd:
                    # spawn new thread and start a console
                    request, client_address = s.accept()
                    thread.start_new_thread(self.start_console, (request, client_address))
    # }

# any handler class must be a subclass of BaseHandlerClass
class BaseHandlerClass: # {
    def __init__(self, session_id, client_addr, request, queue):
        self.session_id = session_id
        self.client_address = client_addr
        self.request = request
        self.queue = queue

    def __del__(self):
        # XXX why isn't this desctructor excuted when exit is called from
        # alarm_handler() in ../server.py?
        self.update_stats('time_disconnected', time.time(), flag=SelectServer.STATS_SET)
        print "IN DESTRUCTOR!!"

        request.close()
        queue.close()
        queue.join_thread()
        
    # subclass can override this one
    def setup(self, args):
        pass

    # subclass must override this one
    def handle(self, args):
        pass

    # subclass can override this one
    def finish(self, args):
        pass

    def update_stats(self, key, value, flag):
        p = (self.client_address[0], self.session_id, key, value, flag)
        print "key: %s, flag: %d" % (p[2], p[4])
        self.queue.put(p)

    def sendall(self, data):
        size = len(data)
        self.request.sendall(data)

        self.update_stats('bytes_sent', size, SelectServer.STATS_ADD)

    def recv(self, max_size=None):
        if max_size:
            ret = self.request.recv(max_size)
        else:
            ret = self.request.recv()
        
        self.update_stats('bytes_received', len(ret), SelectServer.STATS_ADD)

        return ret
# }
