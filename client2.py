import pubsubc
import sys

def myoutput(msg):
    print (f"my callback --- : {msg}")
def myotheroutput(msg):
    print (f"my other callback --- : {msg}")
skt = 9989 if len(sys.argv) == 1 else int(sys.argv[1])
p = pubsubc.PubSub(skt, myoutput, "client2")
p.subscribe("birds", myoutput)
p.list_topics()
p.list_topics()
p.publish("birds", "a_bird_message")
p.publish("birds", "tweet")
p.publish("reptiles", "growl")
p.publish("birds", "2_more_a_bird_message")
p.publish("birds", "2_more_b_bird_message")
import time
time.sleep(15)
p.subscribe("reptiles", myotheroutput)
p.publish("birds", "2_more_c_bird_message")
p.publish("birds", "2_more_d_bird_message")
p.publish("reptiles", "2_reptile_event")
# done
time.sleep(25)
x = input("done ..>")
p.release()