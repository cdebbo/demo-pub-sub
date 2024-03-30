import socket
import sys
import queue
import threading
import _thread
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', int(sys.argv[1])))
in_q = queue.Queue()
out_q = queue.Queue()
sock_lock = _thread.allocate_lock()
def socket_in():
    print ('starting socket in')
    while True:
        print ('waiting to read queue data from socket in')
        #sock_lock.acquire()
        r = sock.recv(8192)
        #sock_lock.release()
        in_q.put_nowait(r.decode('utf-8'))
        print (f"socket_in read {r.decode('utf-8')[:10]}, items in queue: {in_q.qsize()}")
def socket_out():
    print ('starting socket out')
    while True:
        print ('waiting to get queue data for socket out')
        o = out_q.get()
        print (f'  something in the out queue {out_q.qsize()}')
        #sock_lock.acquire()
        print (f'  sending it')
        r = sock.sendall(bytes(o, 'utf-8'))
        #sock_lock.release()
        print (f"socket_out write {o[:10]}, items in queue: {out_q.qsize()}")

print ("connected to server)")

reader = threading.Thread(target=socket_in)
#reader.daemon(lambda x: True)
writer = threading.Thread(target=socket_out)
#writer.daemon(lambda x: True)
reader.start()
writer.start()
print ("threads started")

while True:
    print ("")
    x = input(" > ")
    if x == "quit":
        break
    out_q.put_nowait(x)
    print (f"queue in size {in_q.qsize()}, queue out size {out_q.qsize()}")
    while True:
        if in_q.qsize == 0:
            break
        try:
            x = in_q.get_nowait()
        except queue.Empty:
            break
        else:
            print (f"received: {x}")

sock.close()

sys.exit()
data = """a af
asfjaksdf
dfa
fa
sf"""
for line in data.splitlines():
    sock.sendall(bytes(line, 'utf-8'))
    print (f"sent: {line}")
    r = sock.recv(8192)
    print (f"received: {r.decode('utf-8')}")
sock.close()