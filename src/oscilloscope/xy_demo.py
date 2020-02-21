import argparse
import logging
import sys
import time

from awg.signal_generator import SignalGenerator
from oscilloscope import Oscilloscope

LOGGER = logging.getLogger(__file__)

AWG_LEVEL_FULL = 1.0
AWG_LEVEL_SMALL = AWG_LEVEL_FULL / 5.0

SCOPE_LEVEL_FULL = 0.1


def _awg_init(addr: str) -> SignalGenerator:
    awg = SignalGenerator(addr)
    # awg.write('COUPLING TRACE,OFF,STATE,ON,BSCH,CH1,FCOUP,OFF,PCOUP,ON,ACOUP,ON')
    time.sleep(2)
    for channel in range(1, 3):
        awg.set_amplitude(channel, AWG_LEVEL_SMALL)
        awg.set_output(channel, True)
        time.sleep(1)
    return awg


def _scope_init(addr: str) -> Oscilloscope:
    scope = Oscilloscope(addr)
    scope.write("XY_DISPLAY ON; ACQUIRE_WAY SAMPLING")
    scope.write("TIME_DIV 10US")
    scope.write("GRID_DISPLAY OFF")
    time.sleep(0.2)
    for channel in range(1, 3):
        scope.write(f"BANDWIDTH_LIMIT C{channel}, ON")
        scope.write(f"C{channel}:VOLT_DIV {SCOPE_LEVEL_FULL}")
    scope.write("MENU OFF")
    return scope


def _sine(awg, ratio, offset=0):
    f = 100000
    awg.set_frequency(f, 1)
    awg.set_frequency(f * ratio + offset, 2)


def _move_around(awg,
                 x0: float = 0,
                 y0: float = 0,
                 xd: float = 0.02,
                 yd: float = 0.02,
                 border: float = 0.3,
                 cycles: int = 200):
    x = x0
    y = y0
    for c in range(cycles):
        if abs(x + xd) > AWG_LEVEL_FULL - border:
            xd *= -1
        if abs(y + yd) > AWG_LEVEL_FULL - border:
            yd *= -1
        x += xd
        y += yd
        awg.set_offset(1, x)
        awg.set_offset(2, y)
        time.sleep(0.2)


def run(args: argparse.Namespace):
    DELAY = 2
    scope = _scope_init(args.config['oscilloscope'].get('address'))
    awg = _awg_init(args.config['awg'].get('address'))

    LOGGER.info("Start demo!")

    _sine(awg, 1, 0.4)
    _move_around(awg, x0=0.1, xd=0.025)
    for channel in range(1, 3):
        awg.set_amplitude(channel, AWG_LEVEL_FULL)
        awg.set_offset(channel, 0.0)

    for ratio in [1, 2, 3, 4, 5, 4, 3, 2, 1, 0.5]:
        _sine(awg, ratio, 1)
        time.sleep(DELAY)
        _sine(awg, ratio, -1)
        time.sleep(DELAY)

    for ratio in [1.1, 1.2, 1.5, 1.6, 2, 4]:
        _sine(awg, ratio, 0.01)
        time.sleep(DELAY)

    LOGGER.info("The end!")
    sys.stdin.readline()  # Wait enter

    awg.close()
    scope.close()
    LOGGER.info('Bye!')
