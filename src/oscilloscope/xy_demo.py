import argparse
import logging

from awg.signal_generator import SignalGenerator
from oscilloscope import Oscilloscope

LOGGER = logging.getLogger(__file__)


def _awg_init(addr: str) -> SignalGenerator:
    awg = SignalGenerator(addr)
    awg.write('COUPLING TRACE,OFF, PCOUP,ON, ACOUP,ON')
    awg.write("C1:BASIC_WAVE AMP,1.0")
    return awg


def _scope_init(addr: str) -> Oscilloscope:
    scope = Oscilloscope(addr)
    return scope


def run(args: argparse.Namespace):
    awg = _awg_init(args.config['awg'].get('address'))
    scope = _scope_init(args.config['oscilloscope'].get('address'))

    awg.close()
    scope.close()
    LOGGER.info('Bye!')
