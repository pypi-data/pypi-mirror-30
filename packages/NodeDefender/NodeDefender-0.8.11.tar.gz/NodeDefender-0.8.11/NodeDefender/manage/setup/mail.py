from NodeDefender.manage.setup import (manager, print_message, print_topic,
                                       print_info)
from flask_script import prompt
import NodeDefender


@manager.command
def mail():
    print_topic("Mail")
    print_info("Mail can be used for registering users. Can also be used\
               for password- recovery, sending group- infomation, updates\
               about Nodes, icpes, sensors and much mode")
    enabled = None
    while enabled is None:
        enabled = prompt("Enable Mail(Y/N)").upper()
        if 'Y' in enabled:
            enabled = True
        elif 'N' in enabled:
            enabled = False
        else:
            enabled = None
    if not enabled:
        NodeDefender.config.mail.set(enabled=False)
        if NodeDefender.config.mail.write():
            print_info("Mail- config successfully written")
        return False

    host = None
    while host is None:
        host = prompt("Enter Server Address")

    port = None
    while port is None:
        port = prompt("Enter Server Port")

    tls = None
    while tls is None:
        tls = prompt("TLS Enabled(Y/N)?")
        if tls[0].upper() == 'Y':
            tls = True
        elif tls[0].upper() == 'N':
            tls = False
        else:
            tls = None

    ssl = None
    while ssl is None:
        ssl = prompt("SSL Enabled(Y/N)?")
        if ssl[0].upper() == 'Y':
            ssl = True
        elif ssl[0].upper() == 'N':
            ssl = False
        else:
            ssl = None

    username = None
    while username is None:
        username = prompt('Username')

    password = None
    while password is None:
        password = prompt('Password')

    NodeDefender.config.mail.set(enabled=True,
                                 host=host,
                                 port=port,
                                 tls = tls,
                                 ssl = ssl,
                                 username = username,
                                 password = password)
    if NodeDefender.config.mail.write():
        print_info("Mail- config successfully written")
    return True
