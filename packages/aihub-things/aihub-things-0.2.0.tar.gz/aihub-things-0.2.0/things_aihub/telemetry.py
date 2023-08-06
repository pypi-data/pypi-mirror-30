from __future__ import print_function
from __future__ import unicode_literals
from .session import MqttSession
import json

class Mqtt(MqttSession):
    def upload(self, payload):
        self.client.connect(self.host, self.port, self.keepalive)
        self.client.publish("v1/devices/me/telemetry", json.dumps(payload), 1)