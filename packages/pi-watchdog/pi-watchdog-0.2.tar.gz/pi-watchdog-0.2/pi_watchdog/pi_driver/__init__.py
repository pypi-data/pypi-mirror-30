from pi_watchdog.pi_driver.orange_pi_one import RigDriver as OrangeRigDriver
from pi_watchdog.pi_driver.stub import RigDriver as StubRigDriver
from pi_watchdog.pi_driver.orange_pi_one import BlinkerDriver as OrangeBlinkerDriver
from pi_watchdog.pi_driver.stub import BlinkerDriver as StubBlinkerDriver


def get_rig_dirver(pi_config):
    if pi_config['driver'] == 'orange_pi_one':
        return OrangeRigDriver(pi_config)
    elif pi_config['driver'] == 'stub':
        return StubRigDriver(pi_config)


def get_blinker_driver(pi_config):
    if pi_config['driver'] == 'orange_pi_one':
        return OrangeBlinkerDriver(pi_config)
    elif pi_config['driver'] == 'stub':
        return StubBlinkerDriver(pi_config)