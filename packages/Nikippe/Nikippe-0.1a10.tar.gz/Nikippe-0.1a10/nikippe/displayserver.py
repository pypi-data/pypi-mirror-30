from pelops import mypyyaml
from pelops.mqttclient import MQTTClient
from pelops.epapermqttmessageconverter import EPaperMQTTMessageEncoder
import argparse
import os
import nikippe
from pathlib import Path
import time
import datetime
import threading
from PIL import ImageOps, Image
from nikippe.renderer.renderer import Renderer


class DisplayServer:
    _verbose = None
    _config = None
    _is_stopped = None
    _lock_update = None

    _mqtt_client = None
    _renderer = None

    _send_interval = None
    _activate_loop = None
    _last_timestamp = None
    _stop = None
    _loop_thread = None

    _send_on_change = None
    _update_available = None
    _update_thread = None

    _topic_pub_epaper_full_image = None
    _topic_pub_epaper_full_image_twice = None

    _wipe_at_startup = None
    _wipe_regularly = None
    _wipe_every_nth_day = None
    _wipe_time = None
    _wipe_next_wipe = None

    def __init__(self, config, verbose):
        self._verbose = verbose
        self._config = config["display-server"]
        if self._verbose:
            print("DisplayServer.__init__ - initializing DisplayServer ('{}').".format(self._config))
        self._is_stopped = threading.Event()
        self._is_stopped.set()

        self._mqtt_client = MQTTClient(config["mqtt"], self._verbose)
        self._renderer = Renderer(config["renderer"], self._verbose, self._mqtt_client)

        self._stop = threading.Event()
        self._stop.clear()
        self._set_send_interval(int(self._config["send-interval"]))
        self._set_on_change(bool(self._config["send-on-change"]))

        self._lock_update = threading.Lock()

        self._topic_pub_epaper_full_image = self._config["epaper_full_image"]
        self._topic_pub_epaper_full_image_twice = self._config["epaper_full_image_twice"]

        self._wipe_at_startup = bool(self._config["wipe-screen"]["at-start-up"])
        self._wipe_every_nth_day = int(self._config["wipe-screen"]["every-nth-day"])
        if self._wipe_every_nth_day < 0:
            raise ValueError("DisplayServer.__init__ - 'display-server.wipe-screen.every-nth-day' must be >= 0. ('{}')".
                             format(self._wipe_every_nth_day))
        elif self._wipe_every_nth_day == 0:
            self._wipe_regularly = False
        else:
            self._wipe_regularly = True
            self._wipe_every_nth_day = datetime.timedelta(days=self._wipe_every_nth_day)
            self._wipe_time = datetime.datetime.strptime(self._config["wipe-screen"]["time"], "%H:%M").time()
            self._wipe_next_wipe = datetime.datetime.now() - self._wipe_every_nth_day  # init value for nextwipe - _Set_next_wipe needs this
            self._set_next_wipe()

        if self._verbose:
            print("DisplayServer.__init__ - done.")

    def _set_next_wipe(self):
        self._wipe_next_wipe = datetime.datetime.combine(self._wipe_next_wipe.date() + self._wipe_every_nth_day,
                                                         self._wipe_time)

        while self._wipe_next_wipe <= datetime.datetime.now():
            #  especially on the first day of execution it might happen, that the initial next wipe time stamp has
            #  already been passed -> this would mean that immediatly with the first update a wipescreen would be
            #  performed. this is an unwanted behavior.
            self._wipe_next_wipe = self._wipe_next_wipe + self._wipe_every_nth_day

        if self._verbose:
            print("DisplayServer._set_next_wipe - next wipe will be performed after '{}'.".format(self._wipe_next_wipe))

    def _set_send_interval(self, interval):
        if self._verbose:
            print("DisplayServer._set_send_interval - setting send interval to '{}'.".format(interval))
        self._send_interval = interval
        if self._send_interval < 0:
            raise ValueError("DisplayServer.__init__ - send-interval must be >=0 (currently {}).".
                             format(self._send_interval))
        if self._send_interval == 0:
            self._activate_loop = False
        else:
            self._activate_loop = True
        self._loop_thread = threading.Thread(target=self._poll_loop)

    def _set_on_change(self, on_change):
        if self._verbose:
            print("DisplayServer._set_on_change - set value to '{}'.".format(on_change))
        self._send_on_change = on_change
        self._update_available = self._renderer.update_available
        self._update_thread = threading.Thread(target=self._update_available_detection)

    def _update_available_detection(self):
        if self._verbose:
            print("DisplayServer._update_available_detection - wait for updates.")

        while not self._stop.isSet():
            if self._update_available.wait(0.5):
                self._update()

    def _wipe_screen(self):
        if self._verbose:
            print("DisplayServer._wipe_screen - begin")
        with self._lock_update:
            # simple images for wiping
            # img_white = Image.new('1', (self._renderer._width, self._renderer._height), 255)
            # img_black = Image.new('1', (self._renderer._width, self._renderer._height), 0)

            # current image for wiping
            img_white = self._renderer.current_image
            img_black = ImageOps.invert(img_white.convert('L'))  # ImageOps.invert does not work with b/w mode '1'.
            img_black = img_black.convert('1')  # set image back to b/w mode '1'.

            msg_white = EPaperMQTTMessageEncoder.to_full_image_message(img_white)
            msg_black = EPaperMQTTMessageEncoder.to_full_image_message(img_black)
            for x in range(4):
                if self._verbose:
                    print("DisplayServer._wipe_screen - sending black&white combination (cycle {}).".format(x))
                self._mqtt_client.publish(self._topic_pub_epaper_full_image_twice, msg_black)
                time.sleep(5)
                self._mqtt_client.publish(self._topic_pub_epaper_full_image_twice, msg_white)
                time.sleep(5)
        if self._verbose:
            print("DisplayServer._wipe_screen - end")

    def _calc_sleep_time(self):
        current_time = time.time()
        next_timestamp = self._last_timestamp + self._send_interval
        sleep_time = next_timestamp - current_time
        if self._verbose:
            print("DisplayServer._calc_sleep_time - seconds to next interval: '{} s' ({}).".
                  format(sleep_time, current_time))
        return sleep_time

    def _poll_loop(self):
        if self._verbose:
            print("DisplayServer._poll_loop - entered poll_loop method.")

        self._last_timestamp = time.time()

        while not self._stop.isSet():
            print("update DisplayServer @ {}.".format(time.time()))
            self._update()
            sleep_for = self._calc_sleep_time()
            if self._verbose:
                print("DisplayServer._poll_loop - sleep for " + str(sleep_for) + " seconds.")
            self._stop.wait(sleep_for)
            self._last_timestamp = time.time()

        if self._verbose:
            print("DisplayServer._poll_loop - exiting poll_loop method.")

    def _update(self):
        if self._verbose:
            print("DisplayServer._update - getting new image and publishing it")
        with self._lock_update:
            self._renderer.update()
            img = self._renderer.current_image
            msg = EPaperMQTTMessageEncoder.to_full_image_message(img)
            self._mqtt_client.publish(self._topic_pub_epaper_full_image, msg)
        if self._wipe_regularly:
            if datetime.datetime.now() >= self._wipe_next_wipe:
                self._wipe_screen()
                self._set_next_wipe()
        if self._verbose:
            print("DisplayServer._update - done")

    def start(self):
        if self._verbose:
            print("DisplayServer.start - starting")
        self._is_stopped.clear()
        self._mqtt_client.connect()
        self._mqtt_client.is_connected.wait()
        self._renderer.start()
        self._stop.clear()

        if self._wipe_at_startup:
            self._wipe_screen()

        if self._activate_loop:
            if self._verbose:
                print("DisplayServer.start - activate loop")
            self._loop_thread.start()
        if self._send_on_change:
            if self._verbose:
                print("DisplayServer.start - activate on-update")
            self._update_thread.start()

        if self._verbose:
            print("DisplayServer.start - started")

    def stop(self):
        if self._verbose:
            print("DisplayServer.stop - stopping")

        self._stop.set()
        if self._activate_loop:
            self._loop_thread.join()
        if self._send_on_change:
            self._update_thread.join()

        self._renderer.stop()
        self._mqtt_client.disconnect()
        self._mqtt_client.is_disconnected.wait()
        self._is_stopped.set()
        if self._verbose:
            print("DisplayServer.stop - stopped")

    @classmethod
    def _args_to_config(cls, args=None):
        """Handle command line arguments and read the yaml file into a json structure (=config)."""
        desc = "General purpose display server."
        ap = argparse.ArgumentParser(description=desc)
        ap.add_argument('-c', '--config', type=str, help='yaml config file', required=True)
        ap.add_argument('-v', '--verbose', help='verbose', action="store_true")
        ap.add_argument('--version', action='version',
                            version='%(prog)s {}'.format(nikippe.version),
                            help='show the version number and exit')
        if args:
            arguments = vars(ap.parse_args(args))
        else:
            arguments = vars(ap.parse_args())

        verbose = False
        if arguments["verbose"]:
            verbose = True

        config_filename = arguments["config"]
        config_file = Path(config_filename)
        if not config_file.is_file():
            raise FileNotFoundError("config file '{}' not found.".format(config_filename))

        config = mypyyaml.load(open(config_filename, 'r'), Loader=mypyyaml.Loader)

        try:
            credentials_mqtt = mypyyaml.load(open(os.path.expanduser(config["mqtt"]["mqtt-credentials"]), 'r'),
                                        Loader=mypyyaml.Loader)
        except KeyError:
            pass
        else:
            config["mqtt"].update(credentials_mqtt["mqtt"])

        return config, verbose

    @classmethod
    def standalone(cls, args=None):
        """Public method to start this driver directly. Instantiates an MQTT client and creates an object for the
                given driver."""
        config, verbose = DisplayServer._args_to_config(args)
        config = mypyyaml.dict_deepcopy_lowercase(config)
        displayserver = DisplayServer(config, verbose)
        displayserver.start()
        try:
            while not displayserver._is_stopped.wait(0.1):  # timeout is necessary for CTRL+C
                pass
        except KeyboardInterrupt:
            pass
            displayserver.stop()


def standalone():
    DisplayServer.standalone()


if __name__ == "__main__":
    DisplayServer.standalone()
