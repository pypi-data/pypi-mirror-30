from nikippe.renderer.aelementmqtt import AElementMQTT
from PIL import ImageDraw
import time
import collections
import threading


def avg(iterable):
    if len(iterable) == 0:
        return 0
    return sum(iterable)/len(iterable)


def median(iterable):
    if len(iterable) == 0:
        return 0
    pos = int(len(iterable)/2)
    return iterable[pos]


class Chart(AElementMQTT):
    _history = None
    _history_lock = None
    _aggregation = None
    _aggregator = None
    _group_by = None
    _aggregation_timestamp = None

    _border_top = None
    _border_bottom = None
    _border_left = None
    _border_right = None
    _x1, _y1, _x2, _y2 = [None] * 4

    _chart_length = None
    _chart_height = None
    _chart_pixel_per_value = None
    _chart_connect_values = None

    def __init__(self, config, verbose, update_available, mqtt_client):
        AElementMQTT.__init__(self, config, verbose, update_available, mqtt_client)

        self._group_by = int(self._config["group-by"])
        if self._group_by < 0:
            raise ValueError("Chart.__init__ - 'group-by' must be none-negative. ({})".format(self._group_by))
        try:
            if self._config["aggregator"] == "avg":
                self._aggregator = avg
            elif self._config["aggregator"] == "min":
                self._aggregator = min
            elif self._config["aggregator"] == "max":
                self._aggregator = max
            elif self._config["aggregator"] == "median":
                self._aggregator = median
            else:
                raise ValueError("Chart.__init__ - unknown aggregator '{}'.".format(self._aggregator))
        except ValueError:
            if self._group_by>0:
                raise ValueError("Chart.__init__ - no aggregator provided. must be set if group-by>0.")

        self._border_bottom = self._config["border-bottom"]
        self._border_left = self._config["border-left"]
        self._border_right = self._config["border-right"]
        self._border_top = self._config["border-top"]

        self._chart_connect_values = bool(self._config["connect-values"])
        self._chart_pixel_per_value = int(self._config["pixel-per-value"])
        if self._chart_pixel_per_value <= 0:
            raise ValueError("Chart.__init__ - 'pixel-per-value' must be > 0 ('{}').".
                             format(self._chart_pixel_per_value))
        elif self._chart_pixel_per_value >= self._width:
            raise ValueError("Chart.__init__ - 'pixel-per-value' ({}) must be smaller than the width ({}).".
                             format(self._chart_pixel_per_value, self._width))

        self._aggregation = []
        self._update_margins()

    def _update_margins(self):
        self._x1 = 0
        self._y1 = 0
        self._x2 = self._width - 1
        self._y2 = self._height - 1

        if self._border_top:
            self._y1 += 1
        if self._border_right:
            self._x2 -= 1
        if self._border_left:
            self._x1 += 1
        if self._border_bottom:
            self._y2 -= 1

        self._chart_length = self._x2 - self._x1 + 1
        self._chart_height = self._y2 - self._y1

        self._history = collections.deque(maxlen=self._chart_length)
        self._history_lock = threading.Lock()

    def _topic_sub_handler(self, value):
        value = float(value)
        if self._verbose:
            print("Chart._topic_sub_handler - received value '{}'.".format(value))
        t = time.time()
        if self._aggregation_timestamp + self._group_by <= t:  # new epoch - add old value to history/clear aggregation
            self._aggregation_timestamp = t
            self._aggregation_to_history()
        self._aggregation.append(value)

    def _aggregation_to_history(self):
        aggregation = self._aggregator(self._aggregation)
        with self._history_lock:
            self._history.append(aggregation)
        if self._verbose:
            print("Chart._aggregation_to_history - add value: {}, len history: {}".
                  format(aggregation, len(self._history)))
        self._aggregation.clear()
        self._update_available.set()

    def start(self):
        if self._verbose:
            print("Chart.start()")
        with self._history_lock:
            self._history.clear()
        self._aggregation.clear()
        self._aggregation_timestamp = time.time()
        self._subscribe()

    def stop(self):
        if self._verbose:
            print("Chart.stop()")
        self._aggregation_timestamp = None
        self._unsubscribe()

    def _draw_border(self, draw):
        if self._border_top:
            draw.line((0, 0, self._width-1, 0), fill=self._foreground_color, width=1)
        if self._border_right:
            draw.line((self._width - 1, 0, self._width - 1, self._height - 1), fill=self._foreground_color, width=1)
        if self._border_left:
            draw.line((0, 0, 0, self._height-1), fill=self._foreground_color, width=1)
        if self._border_bottom:
            draw.line((0, self._height-1, self._width-1, self._height-1), fill=self._foreground_color, width=1)

    def update_image(self):
        try:
            with self._history_lock:
                max_history = max(self._history)
                min_history = min(self._history)
        except ValueError:
            max_history, min_history = 0, 0
        value_range = max_history - min_history
        if self._verbose:
            print("Chart.updateImage() - min: {}, max: {}, range: {}, len: {}, height: {}, y2: {}".
                  format(min_history, max_history, value_range, len(self._history), self._chart_height, self._y2))
        # clear image
        draw = ImageDraw.Draw(self.img)
        draw.rectangle((0, 0, self._width-1, self._height-1), fill=self._background_color)
        self._draw_border(draw)
        x = self._x1
        last_x = x
        last_y = None
        with self._history_lock:
            for value in self._history:
                int_value = value - min_history
                try:
                    norm_value = int_value / value_range
                except ZeroDivisionError:
                    norm_value = 0
                y = self._y2 - int(norm_value * self._chart_height)
                if self._verbose:
                    print("Chart.updateImage() - draw history. value:{}, dot:@({}/{})".format(value, x, y))
                if self._chart_connect_values:
                    if last_y is None:
                        last_y = y
                    draw.line((last_x, last_y, x, y), fill=self._foreground_color, width=1)
                    last_x, last_y = x, y
                else:
                    draw.line((x, y, x, y), fill=self._foreground_color, width=1)
                x += self._chart_pixel_per_value

