import random
import requests

class cfg():
    LOW_TIMEOUT = 150
    HIGH_TIMEOUT = 300

    REQUESTS_TIMEOUT = 50
    HB_TIME = 50
    MAX_LOG_WAIT = 50

def random_timeout():
    return random.randrange(cfg.LOW_TIMEOUT, cfg.HIGH_TIMEOUT) / 1000

def send(addr, route, message):
    url = addr + '/' + route
    try:
        reply = requests.post( 
            url=url,
            json=message,
            timeout=cfg.REQUESTS_TIMEOUT / 1000,
        )
    except Exception as e:
        return None

    if reply.status_code == 200:
        return reply
    else:
        return None