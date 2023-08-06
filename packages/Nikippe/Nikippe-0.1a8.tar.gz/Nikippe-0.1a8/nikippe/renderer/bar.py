from nikippe.renderer.aelementmqtt import AElementMQTT
from enum import Enum
from PIL import ImageDraw


class Orientation(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

    @classmethod
    def factory(cls, name):
        name = name.lower()
        if name == "up":
            return cls.UP
        elif name == "down":
            return cls.DOWN
        elif name == "left":
            return cls.LEFT
        elif name == "right":
            return cls.RIGHT
        else:
            raise ValueError("Unknown value '{}'.".format(name))


class Bar(AElementMQTT):
    _current_value = None
    _min_value = None
    _max_value = None
    _value_range = None
    _draw_border  = None
    _orientation = None
    _bar_size = None

    def __init__(self, config, verbose, update_available, mqtt_client):
        AElementMQTT.__init__(self, config, verbose, update_available, mqtt_client)

        self._draw_border = self._config["border"]
        self._orientation = Orientation.factory(self._config["orientation"])
        self._update_bar_size()

        self._max_value = float(self._config["max-value"])
        self._min_value = float(self._config["min-value"])
        self._value_range = self._max_value - self._min_value

        self._current_value = min(self._max_value, max(self._min_value, float(0)))

    def _update_bar_size(self):
        if self._orientation == Orientation.UP or self._orientation == Orientation.DOWN:
            self._bar_size = self._height
        else:
            self._bar_size = self._width
        if self._draw_border:
            self._bar_size = self._bar_size - 2
        if self._bar_size < 1:
            raise ValueError("Bar.__init__ - size of chart must be at least 1 pixel (currently: {}).".
                             format(self._draw_border))

    def _topic_sub_handler(self, value):
        self._current_value = min(self._max_value, max(self._min_value, float(value)))
        if self._verbose:
            print("Bar._topic_sub_handler - received value '{}' -> current value '{}'.".
                  format(value, self._current_value))
        self._update_available.set()

    def start(self):
        if self._verbose:
            print("Bar.start()")
        self._subscribe()

    def stop(self):
        if self._verbose:
            print("Bar.stop()")
        self._unsubscribe()

    def _get_bar_height(self):
        value = self._current_value - self._min_value
        if self._verbose:
            print("Bar._get_bar_height - value: {}, internal value: {}, min: {}, height: {}.".
                  format(self._current_value, value, self._min_value, self._height))
        norm_value = value / self._value_range
        bar_height = int(self._bar_size * norm_value)
        return bar_height

    def update_image(self):
        bar_height = self._get_bar_height()
        if self._verbose:
            print("Bar.updateImage() - value '{}', chart height '{}'".
                  format(self._current_value, bar_height))
        draw = ImageDraw.Draw(self.img)
        draw.rectangle((0, 0, self._width, self._height), fill=self._background_color)
        x1, y1, x2, y2 = 0, 0, self._width-1, self._height-1
        if self._draw_border:
            draw.rectangle((x1, y1, x2, y2), outline=self._foreground_color)
            x1, y1, x2, y2 = x1+1, y1+1, x2-1, y2-1
        if self._orientation == Orientation.UP:
            y1 = y2 - bar_height
        elif self._orientation == Orientation.DOWN:
            y2 = y1 + bar_height
        elif self._orientation == Orientation.LEFT:
            x1 = x2 - bar_height
        elif self._orientation == Orientation.RIGHT:
            x2 = x1 + bar_height
        else:
            raise ValueError("Bar.update_image - don't know how to handle orientation enum '{}'".
                             format(self._orientation))
        if self._verbose:
            print("Bar.updateImage() - rectangle({}, {}, {}, {}).".
                  format(x1, y1, x2, y2))
        draw.rectangle((x1, y1, x2, y2), fill=self._foreground_color)



