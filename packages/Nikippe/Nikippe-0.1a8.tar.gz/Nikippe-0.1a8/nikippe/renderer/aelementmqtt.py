from nikippe.renderer.aelement import AElement


class AElementMQTT(AElement):
    _mqtt_client = None
    _topic_sub = None

    def __init__(self, config, verbose, update_available, mqtt_client):
        AElement.__init__(self, config, verbose, update_available)
        self._mqtt_client = mqtt_client
        self._topic_sub = self._config["topic-sub"]

    def _topic_sub_handler(self, value):
        raise NotImplementedError

    def _subscribe(self):
        self._mqtt_client.subscribe(self._topic_sub, self._topic_sub_handler)

    def _unsubscribe(self):
        self._mqtt_client.unsubscribe(self._topic_sub, self._topic_sub_handler)
