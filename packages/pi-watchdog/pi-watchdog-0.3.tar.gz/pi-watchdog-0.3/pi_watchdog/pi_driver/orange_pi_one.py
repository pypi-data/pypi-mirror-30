from pyA20.gpio import gpio
from pyA20.gpio import port
from time import sleep


class RigDriver(object):
    MAX_LONG_PRESS_PWR_TIME = 10
    PWR_LED_POLL_TIME = 0.1

    PRESS_PWR_BTN_TIME = 0.3
    PRESS_RST_BTN_TIME = 0.3

    def __init__(self, config):
        super(RigDriver, self).__init__()
        gpio.init()
        self.restart_gpio_pin = getattr(port, config['restart_gpio_pin'])
        self.shutdown_gpio_pin = getattr(port, config['shutdown_gpio_pin'])
        self.power_on_led_pin = getattr(port, config['power_on_led_pin'])

    def is_powered_on(self):
        gpio.setcfg(self.power_on_led_pin, gpio.INPUT)
        gpio.pullup(self.power_on_led_pin, gpio.PULLDOWN)
        sleep(0.1)  # pull down here
        if gpio.input(self.power_on_led_pin):
            return True
        return False

    def power_on(self):
        gpio.setcfg(self.shutdown_gpio_pin, gpio.OUTPUT)
        # low level means pressed button
        gpio.output(self.shutdown_gpio_pin, gpio.LOW)
        sleep(self.PRESS_PWR_BTN_TIME)
        # release btn with high level
        gpio.output(self.shutdown_gpio_pin, gpio.HIGH)

    def power_off(self):
        # TODO check if setcfg allways put low level of output
        # it may cause double pwr btn push...
        # to check set high level and then config port once more time
        self.power_on()

    def long_press_power_off(self):
        gpio.setcfg(self.shutdown_gpio_pin, gpio.OUTPUT)
        # low level means pressed button
        gpio.output(self.shutdown_gpio_pin, gpio.LOW)
        gpio.setcfg(self.power_on_led_pin, gpio.INPUT)
        gpio.pullup(self.power_on_led_pin, gpio.PULLDOWN)
        sleep(0.1)  # pull down here

        spent_time = 0
        while spent_time < self.MAX_LONG_PRESS_PWR_TIME:
            if not gpio.input(self.power_on_led_pin):
                # great it is powered off!
                # stop pressing the PWR button
                gpio.output(self.shutdown_gpio_pin, gpio.HIGH)
                return
            sleep(self.PWR_LED_POLL_TIME)
            spent_time += self.PWR_LED_POLL_TIME
        raise Exception('Can not power off RIG.')

    def reset(self):
        # TODO check if setcfg allways put low level of output
        gpio.setcfg(self.restart_gpio_pin, gpio.OUTPUT)
        # low level means pressed button
        gpio.output(self.restart_gpio_pin, gpio.LOW)
        sleep(self.PRESS_RST_BTN_TIME)
        # release btn with high level
        gpio.output(self.restart_gpio_pin, gpio.HIGH)


class BlinkerDriver(object):
    def __init__(self, config):
        super(BlinkerDriver, self).__init__()
        gpio.init()
        self.blinker_gpio_pin = getattr(port, config['blink_pin'])
        self.light_time = 0.4

    def blink(self):
        gpio.setcfg(self.blinker_gpio_pin, gpio.OUTPUT)
        gpio.output(self.blinker_gpio_pin, gpio.HIGH)
        sleep(self.light_time)
        # release btn with high level
        gpio.output(self.blinker_gpio_pin, gpio.LOW)
