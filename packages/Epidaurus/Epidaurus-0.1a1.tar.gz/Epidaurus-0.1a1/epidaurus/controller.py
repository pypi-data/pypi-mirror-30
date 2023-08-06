import argparse
import os
import threading
from pathlib import Path
from pelops import mypyyaml
from pelops.mqttclient import MQTTClient
import epidaurus
from epidaurus.pid import PID


class Controller:
    _config = None
    _verbose = None
    _is_stopped = None

    _topic_sub_set_point = None
    _topic_sub_input = None
    _topic_pub_output = None

    _input = None
    _set_point = None
    _output = None

    _value_idle = None
    _idle_mode_threshold = None

    _pid = None

    def __init__(self, config, verbose):
        self._verbose = verbose
        self._config = config
        if self._verbose:
            print("Controller.__init__ - initializing instance ('{}').".format(self._config))

        self._mqtt_client = MQTTClient(self._config["mqtt"], self._verbose)
        self._pid = PID(self._config["pid"], self._verbose)

        self._topic_pub_output = self._config["topic-pub"]["output"]
        self._topic_sub_input = self._config["topic-sub"]["input"]
        self._topic_sub_set_point = self._config["topic-sub"]["set-point"]
        self._mqtt_client.subscribe(self._topic_sub_set_point, self._sub_set_point_handler)
        self._mqtt_client.subscribe(self._topic_sub_input, self._sub_input_handler())

        self._idle_mode_threshold = float(self._config["controller"]["idle-mode-threshold"])
        self._value_idle = float(self._config["controller"]["value-idle"])

        self._is_stopped = threading.Event()
        self._is_stopped.set()

        if self._verbose:
            print("Controller.__init__ - done.")

    def _sub_input_handler(self, value):
        self._input = value
        self._update()

    def _sub_set_point_handler(self, value):
        self._set_point = value
        self._pid.reset(self._input, self._set_point)
        self._update()

    def _update(self):
        self._output = self._pid.update(self._input)
        if (self._input - self._idle_mode_threshold) > self._set_point:
            # measured value is much higher than target value -> overwriting pid output (but keep pid active)
            self._output = self._value_idle
        self._mqtt_client.publish(self._topic_pub_output, self._output)

    def start(self):
        self._mqtt_client.connect()
        self._mqtt_client.is_connected.wait()
        self._is_stopped.clear()

    def stop(self):
        self._mqtt_client.is_disconnected.wait()
        self._is_stopped.set()

    @classmethod
    def _args_to_config(cls, args=None):
        """Handle command line arguments and read the yaml file into a json structure (=config)."""
        desc = "PID controller for thermostat."
        ap = argparse.ArgumentParser(description=desc)
        ap.add_argument('-c', '--config', type=str, help='yaml config file', required=True)
        ap.add_argument('-v', '--verbose', help='verbose', action="store_true")
        ap.add_argument('--version', action='version',
                            version='%(prog)s {}'.format(epidaurus.version),
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
        config, verbose = Controller._args_to_config(args)
        config = mypyyaml.dict_deepcopy_lowercase(config)
        controller = Controller(config, verbose)
        controller.start()
        try:
            while not controller._is_stopped.wait(0.1):  # timeout is necessary for CTRL+C
                pass
        except KeyboardInterrupt:
            pass
        controller.stop()


def standalone():
    Controller.standalone()


if __name__ == "__main__":
    Controller.standalone()

