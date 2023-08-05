from NodeDefender.mqtt.command import fire, topic_format

def qry(mac_address):
    topic = topic_format.format(mac_address, "sys", "info", "qry")
    return fire(topic, icpe = mac_address)
