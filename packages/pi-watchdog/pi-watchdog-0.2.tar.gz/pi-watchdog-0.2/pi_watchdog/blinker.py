import logging

from pi_watchdog import periodic_task
from pi_watchdog import pi_driver


class BlinkerTask(periodic_task.PeriodicTaskLoop):
    def __init__(self, config):
        self.config = config['blinker']
        self.interval = self.config['interval']
        self.blinker = pi_driver.get_blinker_driver(self.config)
        super(BlinkerTask, self).__init__()

    def execute_periodic_task(self):
        try:
            self.blinker.blink()
        except Exception as e:
            logging.exception("Blinker exception")

    def get_interval(self):
        return self.interval
