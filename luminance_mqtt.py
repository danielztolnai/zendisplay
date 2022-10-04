"""Get or provide ambient lighting data through mqtt"""
import paho.mqtt.client as mqtt
from zendisplay_config import Config
from base_classes import LuminanceSource, Display

class LuminanceMQTT(LuminanceSource, Display):
    """Get ambient lighting information from MQTT"""
    PARAMETER_MQTT_HOST = 'host'
    PARAMETER_MQTT_TOPIC = 'topic'

    def __init__(self, name=None, path=None, host=None):
        super().__init__(name, path)
        self.enabled = False
        self.luminance = 0
        self.mqtt_host = host
        # Create MQTT client
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    @classmethod
    def detect(cls, parameters):
        """Add given MQTT configuration"""
        topic = Config().get('mqtt', 'topic')
        host = Config().get('mqtt', 'host')
        if host is None:
            return
        yield cls(name="mqtt", path=topic, host=host)

    def get_luminance(self):
        """Get last luminance data received"""
        return self.luminance

    def enable(self):
        """Enable the source"""
        super().enable()
        self.client.connect(self.mqtt_host, 1883, 60)
        self.client.loop_start()

    def disable(self):
        """Disable the source"""
        super().disable()
        self.client.loop_stop(force=False)
        self.client.disconnect()

    def on_connect(self, _1, _2, _3, _4):
        """Called when connection is established to the MQTT server"""
        self.client.subscribe(self.path)
        self._set_ready(True)

    def on_message(self, _1, _2, msg):
        """Called when message is received from the MQTT server"""
        self.luminance = int(msg.payload)

    def on_disconnect(self, _1, _2, reason_code, _4):
        """Called when MQTT is disconnected"""
        if reason_code is not mqtt.MQTT_ERR_SUCCESS:
            self._set_ready(False)

    def get_brightness(self):
        """Get current brightness of the display"""
        if self.enabled:
            return self.luminance
        return None

    def set_brightness(self, brightness):
        """Set brightness of the display"""
        if brightness == self.get_brightness() or brightness < 0:
            return

        if self.enabled:
            self._set_brightness(brightness)

    def _set_brightness(self, brightness):
        """Publish given data to the topic of the object"""
        self.client.publish(self.path, brightness)
