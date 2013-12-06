#!/usr/bin/python

import socket
import sys
import json

commands = [
    'help',
    'quit',
]

try:
    import readline

    def completer(text, state):

        options = [x for x in commands if x.startswith(text)]
        if state < len(options):
            return options[state]
        else:
            return None

    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")
except ImportError:
    pass

def menu(client):
    while True:
        try:
            command = raw_input('> ')
            command = command.strip().split()

            if not command:
                continue

            if command[0] == 'help':
                print commands
            elif command[0] == 'quit' or command[0] == 'bye':
                sd.sendall("bye")
                break
            else:
                sd.sendall(command[0])
                print json.dumps(json.loads(sd.recv(1024)), indent=4)

        except EOFError:
            break

HOST = "localhost"
PORT = 1233
if len(sys.argv) > 1:
    HOST = sys.argv[1]

sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sd.connect((HOST, PORT))

sd.sendall('get_commands')
data = json.loads(sd.recv(1024))
cmds = [str(i) for i in data]
commands = commands + cmds

menu(sd)
sd.close()
sys.exit(0)
