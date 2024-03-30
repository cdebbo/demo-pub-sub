import socket
import select
import sys
MAX_BUFFER = 256

class Topic():
    """
    A topic is named channel for messages. Clients can subscribe to topics and clients
    can post messages to topics.
    """
    def __init__(self, name):
        self.name = name
        self.recent_msgs = []
        self.msgs_sent = 0
        self.msgs_recd = 0
        self.clients = set()
    def add_sub(self, c):
        self.clients.add(c)
    def remove_sub(self, c):
        self.clients.remove(c)

topics = {}

class Msg():
    def __init__(self, c, m, dir = 'in'):
        self.client = c
        self.message = m  # str, not bytes
        self.dir = dir
    def __repr__(self):
        return f"C: {self.client}   D: {self.dir}   M: {str(self.message)}"

messages = []

class Client():
    def __init__(self, s, a=None, n = ""):
        self.name = n
        self.socket = s
        self.address = a
    def __repr__(self):
        return f"C: {self.name}: {self.address}"
    def close(self):
        self.socket.close()
        for t in topics:
            if self in t.clients:
                t.remove_sub(self)
        clients.remove(self)

clients = []

# create the pub sub server on the argv[1] number
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('',int(sys.argv[1])))
sock.listen(5)

# create a general system topic. Clients are automatically 
# subscribed to the system topic.
system_topic = Topic("system")
topics[system_topic.name] = system_topic

"""
The server runs forever.
The server listens for data from any client and the server
checks for any pending data to be sent to a client.

Incoming data is marshalled into a Msg() and outgoing data is
sent to the intended client(s)

Finally the server reviews all incoming messags, processes any commands
and prepares any outgoing Msg()s

The server is not multi-threaded and the data is not particularly well specificed.
Each 'packet' is prefixed with a '|' to delimit messages, and no attempt is made
to reassemble large (> MAX_BUFFER) data into messages. Invalid commands are simply dropped
and no retransmission or non-ascii support exists.
"""
try:
    while True:
        ins = [i.socket for i in clients]
        ins.append(sock) # we must also listen for new clients
        ous = [i.client.socket for i in messages if i.dir == 'out']
        ready_in, ready_out, e = select.select(ins, ous, [])
        for x in ready_in:
            if x is sock:
                newSocket, address = sock.accept()
                c = Client(newSocket, address, str(address[1]))
                clients.append(c)
                print (f'New client from {address}')
            else:
                c = [i for i in clients if i.socket == x]
                if len(c) == 0:
                    print (f' no socket found that matches {x}')
                    raise ValueError
                c = c[0]
                # wait for any incoming data. We already know there is data
                # pending (because we called select()) so this should clear immediately.
                recd = c.socket.recv(MAX_BUFFER)
                if len(recd) > 0:
                    tm = recd.decode("utf-8")
                    # recall that our message delimiter is '|'
                    for i in tm.split("|"):
                        if len(i) == 0:
                            continue
                        messages.append(Msg(c, i, 'in'))
                else:
                    # if we receive zero bytes from a socket that was ready
                    # then we know it is a disconnect indicator.
                    print (f"Client from {c.address} disconnected")
                    c.socket.close()
                    for t in topics.values():
                        if c in t.clients:
                            t.clients.remove(c)
                    clients.remove(c)
                    del c

        # now send any outgoing messages - if the socket is ready. Recall that 'ready_out' is
        # the list of sockets which are ready for transmit

        for m in messages:
            # incoming messages need to be processed first, so we ignore them for now
            if m.dir == 'in' or m.client.socket not in ready_out:
                continue
            if m.message:
                nsent = m.client.socket.send(bytes("|" + m.message, 'utf-8'))
                # notice that we ignore any errors, like if nsent is < len(m.message)
        messages = [m for m in messages if m.dir == 'in']

        # add new commands here
        # for example, return stats on a topic, or restrict who can create topics
        # or issue list* commands, or maybe there are different types of
        # topics that only send to the most recent client, or which hold a recent message history
        # or which emulate an 'echo' command.
        new_messages = []
        for m in messages:
            cmd, *r = m.message.split(" ")
            match cmd:
                case 'list_clients':
                    msg = f"list_clients {','.join([x.name for x in clients])}"
                    new_messages.append(Msg(m.client, msg, 'out'))
                case 'list_topics':
                    msg = f"list_topics {','.join(topics.keys())}"
                    new_messages.append(Msg(m.client, msg, 'out'))
                case 'create_topic':
                    if len(r) > 0 and r[0] not in topics:
                        topics[r[0]] = Topic(r[0])
                case 'delete_topic':
                    if len(r) > 0 and r[0] in topics:
                        del topics[r[0]]
                case 'register':
                    if len(r) > 0:
                        if not any([True for x in clients if x.name == r[0]]):
                            m.client.name = r[0]
                case 'subscribe':
                    if len(r) > 0 and r[0] in topics:
                        topics[r[0]].add_sub(m.client)
                case 'unsubscribe':
                    if len(r) > 0 and r[0] in topics:
                        topics[r[0]].remove_sub(m.client)
                case 'publish':
                    if len(r) > 1 and r[0] in topics:
                        for s in topics[r[0]].clients:
                            topics[r[0]].msgs_sent+=1
                            msg = f"published_message {r[0]} [{m.client.name}]{' '.join(r[1:])}"
                            new_messages.append(Msg(s, msg, 'out'))
                        topics[r[0]].msgs_recd+=1
        messages = new_messages 

finally:
    sock.close()