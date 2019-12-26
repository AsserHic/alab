import argparse
import logging
import sys
import time

from awg.signal_generator import SignalGenerator
from oscilloscope import Oscilloscope

LOGGER = logging.getLogger(__file__)


def _awg_init(addr: str) -> SignalGenerator:
    awg = SignalGenerator(addr)
    awg.write('COUPLING TRACE,OFF,STATE,ON,PCOUP,ON,ACOUP,ON')
    awg.write("C1:BASIC_WAVE AMP,1.0")
    for channel in range(1, 3):
        awg.set_output(channel, True)
    return awg


def _scope_init(addr: str) -> Oscilloscope:
    scope = Oscilloscope(addr)
    scope.write("XY_DISPLAY ON; ACQUIRE_WAY SAMPLING")
    scope.write("TIME_DIV 10US")
    scope.write("GRID_DISPLAY OFF")
    for channel in range(1, 3):
        scope.write(f"BANDWIDTH_LIMIT C{channel}, ON")
        scope.write(f"C{channel}:VOLT_DIV 0.19V")
    return scope


def _sine(awg, ratio, offset = 0):
    f = 100000
    awg.frequency(f, 1)
    awg.frequency(f * ratio + offset, 2)


def run(args: argparse.Namespace):
    scope = _scope_init(args.config['oscilloscope'].get('address'))
    awg = _awg_init(args.config['awg'].get('address'))

    for ratio in [1, 2, 3, 4, 5, 4, 3, 2, 1, 0.5]:
        _sine(awg, ratio, 1)
        time.sleep(1)

    for ratio in [1.1, 1.2, 1.5, 1.6, 2, 4]:
        _sine(awg, ratio)
        time.sleep(1)

    sys.stdin.readline()  # Wait enter

    awg.close()
    scope.close()
    LOGGER.info('Bye!')
