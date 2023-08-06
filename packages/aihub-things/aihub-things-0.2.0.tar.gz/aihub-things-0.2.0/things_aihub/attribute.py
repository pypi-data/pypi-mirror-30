from __future__ import print_function
from __future__ import unicode_literals
from .session import MqttSession
import json

class Mqtt(MqttSession):
    def upload(self, payload):
        self.client.connect(self.host, self.port, self.keepalive)
        self.client.publish("v1/devices/me/attributes", json.dumps(payload), 1)

    def request(self, payload):
        self.client.connect(self.host, self.port, self.keepalive)

        def on_connect(client, userdata, rc, *extra_params):
            self.client.subscribe('v1/devices/me/attributes/response/+')
            self.client.publish('v1/devices/me/attributes/request/1', json.dumps(payload))

        def on_message(client, userdata, msg):
            print('Received Topic: ', msg.topic, 'Message: ', str(msg.payload))
            self.client.disconnect()
            self.msg = msg

        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.loop_forever()
        return self.msg

    def shared_subscribe(self, payload):
        self.client.connect(self.host, self.port, self.keepalive)
        self.client.subscribe('v1/devices/me/attributes')
        self.client.loop_forever()
