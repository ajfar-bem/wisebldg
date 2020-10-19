import json
import zmq
from bemoss_lib.utils.BEMOSS_globals import *
import time


def vip_publish_bulk(topic_message_list):
    #bulk message format
    #should be a list of [(sender,target,topic,message)]

    context = zmq.Context()
    pub_socket = context.socket(zmq.PUB)
    pub_socket.connect(SUB_ADDRESS)
    time.sleep(0.5)
    # need to wait for the pub_socket to fully connect. If messages from UI aren't reaching to Agents(VIP)
    # try increasing this delay. Also, consider sending dummy messages before real messages (sometimes first message is
    #  lost, no matter what). A much better solution is to keep sending sync message until a feedback is obtained. However,
    # this requires also setting up two way communication and is complicated. Hopefully, you never get to that point.
    # If you don't like this, complain to the ZMQ people, because its how they designed this thing.
    for topic_message in topic_message_list:
        sender = topic_message[0]
        target = topic_message[1]
        topic = topic_message[2]
        message_dumps = json.dumps(topic_message[3])
        message = ZMS.join([sender,target,topic,message_dumps])
        pub_socket.send_string(sender + ZMS + target + ZMS + topic + ZMS + message_dumps)
        time.sleep(0.01)

    pub_socket.close()
    context.term()

def vip_publish(sender, target,topic,message):
    vip_publish_bulk([(sender, target, topic,message)])



