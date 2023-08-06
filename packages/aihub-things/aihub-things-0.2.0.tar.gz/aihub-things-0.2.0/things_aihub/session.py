from __future__ import print_function
from __future__ import unicode_literals
import paho.mqtt.client as mqtt
import json

class MqttSession(object):
    def __init__(self, token, host, port=1883, keepalive=60):
        self.host = host
        self.token = token
        self.port = port
        self.keepalive = 60
        self.client = mqtt.Client()
        self.client.username_pw_set(token)

class RestHttpSession(object):
    def __init__(self, device_id, host, jwt_token):
        self.device_id = device_id
        self.host = host
        self.token = jwt_token


class DeviceHttpSession(object):
    pass

class CoapSession(object):
    pass