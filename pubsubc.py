import socket
import queue
import threading
MAX_BUFFER = 256

class PubSub():
    """
    Client side interface to the pub-sub message bus

    Create the client, with the server's socket, a generic systemwide callback for the 'system' topic
    and a client name
    s = PubSub(int(sys.argv[1]), sysprint, "myname")

    publish to a topic with
    s.publish("topic", "message")

    subscribe to a topic with
    s.subscribe("topic", callback)

    Additional commands are listed below
    """
    def __init__(self, server_socket, systemwide_callback, name=""):
        self.name = name
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(('localhost', server_socket))
            print ("Connected to server")
        except ConnectionRefusedError:
            print ("Server may not be running")
            return None
        # queue's hold strings, socket handles bytes. marshall between these
        self.in_q = queue.Queue()
        self.out_q = queue.Queue()
        self.reader = threading.Thread(target=self._socket_in)
        self.manager = threading.Thread(target=self._manage_incoming)
        self.writer = threading.Thread(target=self._socket_out)
        self.reader.start()
        self.writer.start()
        self.manager.start()

        self.topics = {}  # hash of topic and callback
        self.register(name)
        self.subscribe("systemwide", systemwide_callback)

    def _manage_incoming(self):
        """
        Handing messages from the pub sub server.

        We fire the callback for a specific topic or we send the message to the default callback.
        """
        while True:
            mm = self.in_q.get()
            for m in mm.split("|"):
                if len(m) == 0:
                    continue
                c, *r = m.split(" ")
                if c == "published_message" and len(r) > 1 and r[0] in self.topics:
                    # fire off to callback
                    self.topics[r[0]](r[1:])
                elif c == "list_topics" and len(r) > 0:
                    r = f"topics: {r[0]}"
                    self.topics['systemwide'](r)
                elif c == "list_clients" and len(r) > 0:
                    r = f"clients: {r[0]}"
                    self.topics['systemwide'](r)
    def _socket_in(self):
        while True:
            r = self.sock.recv(MAX_BUFFER)
            if r != 0:
              self.in_q.put_nowait(r.decode('utf-8'))
    def _socket_out(self):
        while True:
            o = self.out_q.get()
            o = "|" + o
            r = self.sock.sendall(bytes(o, 'utf-8'))
    
    def release(self):
        self.sock.close()
    def list_topics(self):
        msg = f"list_topics"
        self.out_q.put(msg)
    def list_clients(self):
        msg = f"list_clients"
        self.out_q.put(msg)
    def register(self, name):
        msg = f"register {name}"
        self.out_q.put(msg)
    def publish(self, topic, message):
        msg = f"publish {topic} {message}"
        self.out_q.put(msg)
    def create_topic(self, topic, **kwargs):
        msg = f"create_topic {topic}"
        self.out_q.put(msg)
    def delete_topic(self, topic):
        msg = f"delete_topic {topic}"
        self.out_q.put(msg)
    def subscribe(self, topic, callback, **kwargs):
        if topic not in self.topics:
            self.topics[topic] = callback
            msg = f"subscribe {topic}"
            self.out_q.put(msg)
    def unsubscribe(self, topic):
        if topic in self.topics:
            msg = f"unsubscribe {topic}"
            self.out_q.put(msg)
            del self.topics[topic]
    def get_subscriptions(self):
        return self.topics.keys()

def sysprint(msg):
    print (f"sysprint says: {msg}")