import datetime
import logging
import subprocess
import requests
import time

from pi_watchdog import periodic_task


def watch_router(config, notifier):
    watch_task = RouterWatchTask(config, notifier)
    watch_task.start()
    return watch_task


class RouterWatchTask(periodic_task.PeriodicTaskLoop):
    def __init__(self, config, notifier):
        self.config = config
        self.router_conf = config['watch_router']
        self.interval = int(self.router_conf['ping_frequency'].rstrip('s'))
        self.notifier = notifier
        super(RouterWatchTask, self).__init__()
        self.fails_after_reboot = 0
        self.fails_after_last_success = 0
        self.last_reboot_time = datetime.datetime.now()

    def execute_periodic_task(self):
        if self.is_scheduled_reboot():
            logging.info("ROUTER: Scheduled reboot...")
            self.reboot_router()
            return
        try:
            self.ping(self.router_conf['addr'])
            self.ping(self.router_conf['internet_ping_address'])
        except Exception as e:
            self.fails_after_reboot += 1
            self.fails_after_last_success += 1
            logging.exception(
                "ROUTER: Router health check is failed. Reason {reason}. "
                "fails_after_reboot={fails_after_reboot}, "
                "fails_after_last_success={fails_after_last_success}".format(
                    reason=e.message,
                    fails_after_reboot=self.fails_after_reboot,
                    fails_after_last_success=self.fails_after_last_success
                ))
            restart_on_fails_after_last_success = int(
                self.router_conf['restart_on_fails_after_last_success'])
            if self.fails_after_last_success >= restart_on_fails_after_last_success:
                message = "ROUTER: Max number of fails({}) was reached. Restart router...".format(
                    restart_on_fails_after_last_success)
                logging.error(message)
                self.notifier.add_message(message)
                self.reboot_router()
        else:
            self.fails_after_last_success = 0

    def reboot_router(self):
        logging.info("ROUTER: Rebooting router...")
        proc = subprocess.Popen(self.router_conf['restart_router_str'].split())
        for i in range(10):
            ret_code = proc.poll()
            if ret_code is not None:
                logging.info("ROUTER: Reboot router done.")
                break
            time.sleep(1)
        else:
            logging.info("ROUTER: Reboot router failed.")
        self.fails_after_reboot = 0
        self.fails_after_last_success = 0
        self.last_reboot_time = datetime.datetime.now()

    def is_scheduled_reboot(self):
        now = datetime.datetime.now()
        if self.router_conf.get('scheduled_restart_at') is None:
            return False
        for scheduled_conf_time in self.router_conf['scheduled_restart_at']:
            hour, minute = scheduled_conf_time.split(':')
            scheduled_time = now.replace(hour=int(hour), minute=int(minute))
            if 0 < ((now - scheduled_time).total_seconds() < 300 and
                    (now - self.last_reboot_time).total_seconds() >= 300):
                return True
        return False

    def ping(self, address):
        logging.info("ROUTER: Ping {}".format(address))
        requests.get(address, timeout=1)

    def get_interval(self):
        return self.interval
