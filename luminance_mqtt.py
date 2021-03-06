"""Get or provide ambient lighting data through mqtt"""
from luminance_sources import LuminanceSource

class LuminanceMQTT(LuminanceSource):
    """Get ambient lighting information from MQTT"""
    import paho.mqtt.client as mqtt
    PARAMETER_MQTT_HOST = 'host'
    PARAMETER_MQTT_TOPIC = 'topic'

    def __init__(self, name=None, path=None, host=None):
        super().__init__(name, path)
        self.luminance = 0
        # Create MQTT client
        self.client = self.mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(host, 1883, 60)

    @classmethod
    def detect(cls, parameters):
        """Add given MQTT configuration"""
        topic = parameters[cls.PARAMETER_MQTT_TOPIC]
        host = parameters[cls.PARAMETER_MQTT_HOST]
        if host is None:
            return
        yield cls(name="mqtt", path=topic, host=host)

    def get_luminance(self):
        """Get last luminance data received"""
        return self.luminance

    def enable(self):
        """Enable the source"""
        self.client.loop_start()

    def disable(self):
        """Disable the source"""
        self.client.loop_stop(force=False)

    def on_connect(self, _1, _2, _3, _4):
        """Called when connection is established to the MQTT server"""
        self.client.subscribe(self.path)

    def on_message(self, _1, _2, msg):
        """Called when message is received from the MQTT server"""
        self.luminance = int(msg.payload)

    def publish(self, value):
        """Publish given data to the topic of the object"""
        self.client.publish(self.path, value)
