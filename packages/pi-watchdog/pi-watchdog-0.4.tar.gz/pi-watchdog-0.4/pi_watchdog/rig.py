import datetime
import logging
import re
import time

import requests

from pi_watchdog import periodic_task
from pi_watchdog import pi_driver


def watch_rigs(rig_config, full_config, notifier):
    watch_task = RigWatchTask(rig_config, full_config, notifier)
    watch_task.start()
    return watch_task


class RigWatchTask(periodic_task.PeriodicTaskLoop):
    def __init__(self, rig_config, full_config, notifier):
        self.full_config = full_config
        self.rig_conf = rig_config
        self.interval = int(self.rig_conf['ping_frequency'].rstrip('s'))
        self.notifier = notifier
        super(RigWatchTask, self).__init__()
        self.fails_after_reboot = 0
        self.fails_after_last_success = 0
        self.last_reboot_time = datetime.datetime.now()
        self.pi_driver = pi_driver.get_rig_dirver(self.rig_conf['name'], rig_config['pi'])

    def execute_periodic_task(self):
        try:
            self.watch_power_on()
            self.watch_claymore()
            self.watch_pool_worker()
        except Exception as e:
            self.fails_after_reboot += 1
            self.fails_after_last_success += 1
            logging.exception(
                "RIG {rig_name}: Health check is failed. Reason {reason}. "
                "fails_after_reboot={fails_after_reboot}, "
                "fails_after_last_success={fails_after_last_success}".format(
                    rig_name=self.rig_conf['name'],
                    reason=e.message,
                    fails_after_reboot=self.fails_after_reboot,
                    fails_after_last_success=self.fails_after_last_success
                ))
            restart_on_fails_after_last_success = int(
                self.rig_conf['restart_on_fails_after_last_success'])
            if self.fails_after_last_success >= restart_on_fails_after_last_success:
                err_msg = "RIG {rig_name}: Max number of fails({fails_after_last_success}) was reached. Restart rig...".format(
                    rig_name=self.rig_conf['name'],
                    fails_after_last_success=restart_on_fails_after_last_success
                )
                logging.error(err_msg)
                self.notifier.add_message(err_msg)
                self.reboot_rig()
        else:
            self.fails_after_last_success = 0

    def get_interval(self):
        return self.interval

    def reboot_rig(self):
        return self.reset()

    def reset(self):
        result = self.pi_driver.reset()
        self.fails_after_reboot = 0
        self.fails_after_last_success = 0
        return result

    def shutdown_startup(self):
        return self.pi_driver.power_on()

    def force_shutdown(self):
        return self.pi_driver.long_press_power_off()

    def watch_power_on(self):
        if self.pi_driver.is_powered_on() == False:
            # double check if rig is powered off
            time.sleep(1)
            if self.pi_driver.is_powered_on() == False:
                err_msg = "RIG {rig_name} is powered off. Power on...".format(rig_name=self.rig_conf['name'])
                logging.error(err_msg)
                self.notifier.add_message(err_msg)
                self.pi_driver.power_on()

    def watch_claymore(self):
        if not self.rig_conf['watch_claymore']:
            return
        claymore_url = self.rig_conf['addr'] + ':' + str(self.rig_conf['claymore_port'])
        response = requests.get(claymore_url, timeout=2)
        response.raise_for_status()
        total_speed_occurences = re.findall(r'ETH - Total Speed: \d+.\d+ Mh/s, Total Shares: ', response.text)
        speed_list = map(lambda speed_str: float(speed_str.split()[4]), total_speed_occurences)
        if len(speed_list) == 0:
            raise Exception('No "Total Speed" occurrence!')
        max_total_speed = max(speed_list)
        logging.info('RIG {rig_name} max_total_speed in claymore: {max_total_speed}'.format(
            rig_name=self.rig_conf['name'],
            max_total_speed=max_total_speed))
        if max_total_speed < self.rig_conf['min_claymore_speed']:
            raise Exception('Max "Total Speed" is too small {max_total_speed}. '
                            '"min_claymore_speed" is configured as {min_claymore_speed}'.format(
                max_total_speed=max_total_speed,
                min_claymore_speed=self.rig_conf['min_claymore_speed']
            ))

    def watch_pool_worker(self):
        pass
        #>>> d = requests.get('https://api.nanopool.org/v1/eth/reportedhashrate/0xff8a1ce1885f89885833f10f8d8dbe4bc4af1c0c/580xMaybe7')
        #>>> d.json()
        #{u'status': True, u'data': 175.354}