from nikippe.renderer.chart import Chart
from nikippe.renderer.digitalclock import DigitalClock
from nikippe.renderer.mqtttext import MQTTText
from nikippe.renderer.statictext import StaticText
from nikippe.renderer.bar import Bar


class ElementFactory:
    @staticmethod
    def create_element(config_element, verbose, update_available, mqtt_client):
        element = None
        if config_element["active"]:
            if config_element["type"].lower() == "chart":
                element = Chart(config_element, verbose, update_available, mqtt_client)
            elif config_element["type"].lower() == "statictext":
                element = StaticText(config_element, verbose, update_available)
            elif config_element["type"].lower() == "digitalclock":
                element = DigitalClock(config_element, verbose, update_available)
            elif config_element["type"].lower() == "mqtttext":
                element = MQTTText(config_element, verbose, update_available, mqtt_client)
            elif config_element["type"].lower() == "bar":
                element = Bar(config_element, verbose, update_available, mqtt_client)
            else:
                raise ValueError("ElementFactory.create_element - unknown type '{}'".
                                 format(config_element["type"].lower()))
        else:
            if verbose:
                print("ElementFactory.create_element - skipping inactive element '{}.{}'.".
                      format(config_element["type"].lower(), config_element["name"]))

        return element

    @staticmethod
    def create_elements(config_elements, verbose, update_available, mqtt_client):
        element_list = []

        if verbose:
            print("ElementFactory.create_elements - start")

        for config_element in config_elements:
            element = ElementFactory.create_element(config_element, verbose, update_available, mqtt_client)
            if element is not None:
                element_list.append(element)

        if verbose:
            print("ElementFactory.create_elements - finished")

        return element_list


