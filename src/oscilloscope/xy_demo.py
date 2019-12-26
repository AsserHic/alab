import argparse
import logging
import sys

from awg.signal_generator import SignalGenerator
from oscilloscope import Oscilloscope

LOGGER = logging.getLogger(__file__)


def _awg_init(addr: str) -> SignalGenerator:
    awg = SignalGenerator(addr)
    awg.write('COUPLING TRACE,OFF, PCOUP,ON, ACOUP,ON')
    awg.write("C1:BASIC_WAVE AMP,1.0")
    awg.set_output(1, True)
    awg.set_output(2, True)
    return awg


def _scope_init(addr: str) -> Oscilloscope:
    scope = Oscilloscope(addr)
    scope.write("XY_DISPLAY ON")
    return scope


def _circle(awg):
    awg.frequency(10000, 1)
    awg.frequency(20001, 2)


def run(args: argparse.Namespace):
    scope = _scope_init(args.config['oscilloscope'].get('address'))
    awg = _awg_init(args.config['awg'].get('address'))

    _circle(awg)
    sys.stdin.readline()  # Wait enter

    awg.close()
    scope.close()
    LOGGER.info('Bye!')
