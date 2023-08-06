import threading
from abc import ABCMeta, abstractmethod
import time
import logging


class PeriodicTaskLoop(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self._thread = threading.Thread(target=self.loop)

    def start(self):
        self.running = True
        self._thread.start()

    def stop(self):
        self.running = False

    def join(self):
        while self._thread.is_alive():
            self._thread.join(timeout=1)

    def loop(self):
        while self.running:
            try:
                self.execute_periodic_task()
            except Exception as e:
                logging.exception("Error during execution periodic task.")
            time.sleep(self.get_interval())

    @abstractmethod
    def execute_periodic_task(self):
        pass

    @abstractmethod
    def get_interval(self):
        pass
