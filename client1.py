import pubsubc
import sys

def myoutput(msg):
    print (f"my callback --- : {msg}")
skt = 9989 if len(sys.argv) == 1 else int(sys.argv[1])
p = pubsubc.PubSub(skt, myoutput, "client1")
p.list_topics()
p.create_topic("birds")
p.list_topics()
p.publish("birds", "a bird message")
p.publish("birds", "tweet")
p.create_topic("reptiles")
p.publish("reptiles", "growl")
p.subscribe("birds", myoutput)
p.publish("birds", "more a bird message")
p.publish("birds", "more b bird message")
import time
time.sleep(10)
p.publish("birds", "more_c_bird_message")
p.publish("birds", "more_d_bird_message")
time.sleep(30)
# done
x = input("done ..>")
p.release()