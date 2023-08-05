import NodeDefender

default_config = {'enabled' : False,
                  'host' : '',
                  'port' : '',
                  'database' : ''}

config = default_config.copy()

def load_config(parser):
    config['enabled'] = eval(parser['REDIS']['ENABLED'])
    config['host'] = parser['REDIS']['HOST']
    config['port'] = parser['REDIS']['PORT']
    config['database'] = parser['REDIS']['DATABASE']
    NodeDefender.app.config.update(
        REDIS=config['enabled'],
        REDIS_HOST=config['host'],
        REDIS_PORT=config['port'],
        REDIS_DATABASE=config['database'])
    return True

def set_default():
    config = default_config.copy()

def set(**kwargs):
    for key, value in kwargs.items():
        if key not in config:
            continue
        NodeDefender.config.redis.config[key] = str(value)
    return True

def write():
    NodeDefender.config.parser['REDIS'] = config
    return NodeDefender.config.write()
