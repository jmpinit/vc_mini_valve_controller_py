import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from vc_mini_valve_controller import Microvalve


def test_fire():
    """Connects to VC Mini Valve Controller, sets some parameters, and then fires a test shot"""

    valve_port = os.getenv('VALVE_PORT')

    if valve_port is None:
        raise Exception('Must set VALVE_PORT environment variable to the port path or name before running the test')

    microvalve = Microvalve(valve_port)
    microvalve.init()

    # Setup test parameters
    microvalve.load_parameters(0, 0)
    microvalve.set_peak_time(400)
    microvalve.set_open_time(1000)
    microvalve.set_cycle_time(60000)
    microvalve.set_peak_current(13)
    microvalve.set_shot_count(100)

    # Fire once
    microvalve.single_shot(True, False)


if __name__ == '__main__':
    test_fire()
