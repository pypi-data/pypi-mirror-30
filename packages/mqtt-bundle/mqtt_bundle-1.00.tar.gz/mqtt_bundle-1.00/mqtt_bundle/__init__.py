import zope.event.classhandler
from applauncher.kernel import KernelReadyEvent, Configuration, KernelShutdownEvent, Kernel
import inject
import threading
import paho.mqtt.client as mqtt
import logging


class MqttMessageEvent(object):
    def __init__(self, client, userdata, message):
        self.client = client
        self.userdata = userdata
        self.message = message

class MqttBundle(object):

    def __init__(self):

        self.config_mapping = {
            "mqtt": {
                "host": None
            }
        }

        self.logger = logging.getLogger("mqtt")
        self.client = mqtt.Client()
        self.client.on_message = self._on_message

        self.injection_bindings = {
            mqtt.Client: self.client
        }
        self.lock = threading.Lock()
        zope.event.classhandler.handler(KernelReadyEvent, self.kernel_ready)
        zope.event.classhandler.handler(KernelShutdownEvent, self.kernel_shutdown)

    def _on_message(self, client, userdata, message):
        zope.event.notify(MqttMessageEvent(client, userdata, message))

    def kernel_shutdown(self, event):
        self.logger.info("Disconnecting...")
        self.client.disconnect()
        self.client.loop_stop(force=False)
        self.lock.release()
        self.logger.info("Disconnected")

    @inject.params(config=Configuration)
    @inject.params(kernel=Kernel)
    def kernel_ready(self, event, config, kernel):
        self.client.connect(config.mqtt.host)
        self.client.loop_start()
        self.lock.acquire()
        kernel.run_service(lambda lock: lock.acquire(), self.lock)
        self.logger.info("Connected to {host} and ready".format(host=config.mqtt.host))
