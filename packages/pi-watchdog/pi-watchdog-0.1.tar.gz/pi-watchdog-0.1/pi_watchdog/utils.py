import optparse
import yaml
import logging
import tempfile
import signal


def parse_config_file():
    opt_parser = optparse.OptionParser(
        usage=("usage: %prog [options]"))
    opt_parser.add_option("-c", "--config", dest="config_file",
        help="Config file", type="string", default="/etc/pi-watchdog.conf")
    (options, args) = opt_parser.parse_args()

    with open(options.config_file, "r") as config_file:
        config = yaml.load(config_file)
        return config


def configure_logging(config):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')

    consolelog = logging.StreamHandler()
    consolelog.setLevel(logging.DEBUG)
    consolelog.setFormatter(formatter)
    logger.addHandler(consolelog)

    filelog = logging.FileHandler(config['log']['file'])
    filelog.setLevel(logging.DEBUG)
    filelog.setFormatter(formatter)
    logger.addHandler(filelog)

    mail_file = tempfile.NamedTemporaryFile(delete=True)
    mail_file_log = logging.FileHandler(mail_file.name)
    mail_file_log.setLevel(logging.ERROR)
    mail_file_log.setFormatter(formatter)
    logger.addHandler(mail_file_log)

    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def handle_signals(*watch_tasks):
    def handler(signum, frame):
        logging.info("Received signal {}. Stopping tasks...".format(signum))
        for task in watch_tasks:
            task.stop()

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
