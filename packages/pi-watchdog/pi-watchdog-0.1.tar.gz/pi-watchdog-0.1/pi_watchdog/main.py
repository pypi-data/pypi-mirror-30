#!/usr/bin/env python
# python run.py -c pi-watchdog.yaml

import logging

from pi_watchdog import rig
from pi_watchdog import router
from pi_watchdog import utils
from pi_watchdog import notifier as email_notifier
from pi_watchdog import blinker


def main():
    config = utils.parse_config_file()
    utils.configure_logging(config)
    logging.info("Starting watchdog...")

    notifier = email_notifier.NotifierTask(config)
    notifier.start()

    led_blinker = blinker.BlinkerTask(config)
    led_blinker.start()

    watch_tasks = []
    utils.handle_signals(notifier, led_blinker, *watch_tasks)

    if config.get('watch_router'):
        watch_tasks.append(router.watch_router(config, notifier))
    for rig_conf in config['watch_rigs']:
        rig_watcher = rig.watch_rigs(rig_config=rig_conf, full_config=config, notifier=notifier)
        watch_tasks.append(rig_watcher)

    for task in watch_tasks:
        task.join()

    logging.info("Watchdog exited.")


if __name__ == "__main__":
    main()
