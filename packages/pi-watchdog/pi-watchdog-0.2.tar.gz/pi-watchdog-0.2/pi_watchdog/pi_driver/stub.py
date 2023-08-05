import logging


class RigDriver(object):
    MAX_LONG_PRESS_PWR_TIME = 10
    PWR_LED_POLL_TIME = 0.1

    PRESS_PWR_BTN_TIME = 0.3
    PRESS_RST_BTN_TIME = 0.3

    def __init__(self, config):
        self.restart_gpio_pin = config['restart_gpio_pin']
        self.shutdown_gpio_pin = config['shutdown_gpio_pin']
        self.power_on_led_pin = config['power_on_led_pin']

    def is_powered_on(self):
        logging.info("Is powered on pin {}".format(self.power_on_led_pin))
        return True

    def power_on(self):
        logging.info("Power ON on pin {}".format(self.shutdown_gpio_pin))

    def power_off(self):
        logging.info("Power OFF on pin {}".format(self.shutdown_gpio_pin))

    def long_press_power_off(self):
        logging.info("Long press power off on pin {}".format(self.shutdown_gpio_pin))

    def reset(self):
        logging.info("Reset on pin {}".format(self.restart_gpio_pin))


class BlinkerDriver(object):
    def __init__(self, config):
        super(BlinkerDriver, self).__init__()
        self.blinker_gpio_pin = config['blink_pin']

    def blink(self):
        logging.info("Blink on pin {}".format(self.blinker_gpio_pin))
