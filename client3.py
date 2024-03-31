import pubsubc
import sys
import time

def myoutput(msg):
    print (f"my callback --- : {msg}")
skt = 9989 if len(sys.argv) == 1 else int(sys.argv[1])
p = pubsubc.PubSub(skt, myoutput, "client3")
time.sleep(5)
p.subscribe("reptiles", myoutput)
p.publish("reptiles", "a_bird_message")
p.publish("reptiles", "tweet")
p.publish("reptiles", "growl")
p.publish("reptiles", "3 reptile say hi")
p.publish("reptiles", "3 reptile say hello")
time.sleep(10)
p.publish("reptiles", "3 reptile say hi again")
p.publish("reptiles", "3 reptile say hello again")
p.list_clients()
time.sleep(20)
x = input("done ..>")
p.release()