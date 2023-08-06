from PIL import Image
import threading
import os
from nikippe.renderer.elementfactory import ElementFactory


class Renderer:
    _config = None
    _verbose = None
    _elements = None

    _width = None
    _height = None

    _mqtt_client = None

    current_image = None
    _base_image = None
    _background_image = None

    _lock_update = None
    update_available = None

    def __init__(self, config, verbose, mqtt_client):
        self._verbose = verbose
        self._config = config
        if self._verbose:
            print("Renderer.__init__ - creating instance ('{}').".format(config))
        self._mqtt_client = mqtt_client
        self.update_available = threading.Event()
        self._lock_update = threading.Lock()
        self._elements = ElementFactory.create_elements(self._config["elements"], self._verbose,
                                                        self.update_available, self._mqtt_client)

        self._width = int(self._config["width"])
        self._height = int(self._config["height"])
        self._background_color = int(self._config["background-color"])
        if self._background_color not in [0,255]:
            raise ValueError("Renderer.__init__ - background-color must be 0 or 255 ('{}').".
                             format(self._background_color))

        self._base_image = Image.new('1', (self._width, self._height), self._background_color)
        try:
            self._background_image = Image.open(os.path.expanduser(self._config["background"]))
            self._base_image.paste(self._background_image, (0,0))
        except KeyError:
            pass  # no background image provided in config file
        self.current_image = self._base_image.copy()

        if self._verbose:
            print("Renderer.__init__ - done.")

    def update(self):
        if self._verbose:
            print("Renderer.update - update renderer ... waiting for lock")
        with self._lock_update:
            self.update_available.clear()
            self._update_elements()
            self.current_image = self._merge_elements_to_new_image()
        if self._verbose:
            print("Renderer.update - update renderer ... released lock")

    def _update_elements(self):
        if self._verbose:
            print("Renderer._update_elements - update renderer")
        for element in self._elements:
            try:
                element.update_image()
            except NotImplementedError:
                pass

    def _merge_elements_to_new_image(self):
        if self._verbose:
            print("Renderer._merge_elements - create new image with the renderer")
        new_image = self._base_image.copy()
        for element in self._elements:
            new_image.paste(element.img, (element.x, element.y))
        return new_image

    def start(self):
        if self._verbose:
            print("Renderer.start - starting {} elements.".format(len(self._elements)))
        for e in self._elements:
            try:
                e.start()
            except NotImplementedError:
                pass

    def stop(self):
        if self._verbose:
            print("Renderer.stop - stopping {} elements.".format(len(self._elements)))
        for e in self._elements:
            try:
                e.stop()
            except NotImplementedError:
                pass
