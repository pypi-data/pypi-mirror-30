import paho.mqtt.client as PahoMQTT
from threading import Thread
import NodeDefender

def add(host, port = 1883, username = None, password = None):
    mqtt = MQTT()
    mqtt.host = host
    mqtt.port = port
    NodeDefender.db.mqtt.mark_offline(host, port)
    try:
        mqtt.connect()
    except TimeoutError:
        NodeDefender.mqtt.logger.error("MQTT {}:{} unable to connect".\
                                     format(host, port))
        return False

    NodeDefender.db.mqtt.mark_online(host, port)
    NodeDefender.mqtt.logger.info("MQTT {}:{} initialized".\
                                  format(host, port))
    mqtt.loop_start()
    return True

def load(mqttlist = None):
    if mqttlist is None:
        mqttlist = NodeDefender.db.mqtt.list()

    if len(mqttlist) is 0:
        NodeDefender.mqtt.logger.warning("No MQTT Connection present")

    for m in mqttlist:
        NodeDefender.db.redis.mqtt.load(m)
        Thread(target=add, args=[m.host, m.port]).start()
        NodeDefender.mqtt.logger.info("MQTT {}:{} Loaded".\
                                      format(m.host, m.port))
    return len(mqttlist)

def connection(host, port):
    client = PahoMQTT.Client()
    client.connect(host, port, 60)
    return client

class MQTT:
    def __init__(self):
        self.host = None
        self.port = None
        self.username = None
        self.password = None
        self.client = PahoMQTT.Client()
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect

    def __call__(self):
        if self.online:
            return str(self.host) + ':' + str(self.port)
        else:
            return False

    def loop_start(self):
        if self.host is None:
            raise AttributeError('IP Address not set')
        if self.port is None:
            raise AttributeError('Port not set')
        self.info = {'host' : self.host, 'port' : self.port}
        self.client.loop_start()
    
    def connect(self):
        self.client.connect(str(self.host), int(self.port), 60)
        self.connect = True
        return True

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe('icpe/#')

    def on_message(self, client, userdata, msg):
        NodeDefender.mqtt.message.event(msg.topic,
                                        msg.payload.decode('utf-8'), self.info)
