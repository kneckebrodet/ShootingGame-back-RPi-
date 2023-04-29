import paho.mqtt.client as mqtt

class MQTTClient:
    def __init__(self, broker_address, broker_port, username=None, password=None):
        self.broker_address = broker_address
        self.broker_port = broker_port
        self.username = username
        self.password = password
        self.points = None
        self.client = mqtt.Client()
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")

    def on_message(self, client, userdata, message):
        print(f"Received message '{str(message.payload.decode())}' on topic '{message.topic}'")
        self.points = str(message.payload.decode())
        self.client.disconnect()

    def connect(self):
        self.client.connect(self.broker_address, self.broker_port)

    def publish(self, topic, message):
        self.client.publish(topic, message)

    def subscribe(self, topic):
        self.client.subscribe(topic)
        self.client.loop_forever()
        return int(self.points)