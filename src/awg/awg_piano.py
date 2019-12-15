import logging

from awg.signal_generator import SignalGenerator

LOGGER = logging.getLogger(__file__)


class Piano:

    def __init__(self, addr):
        self.awg = SignalGenerator(addr)

    def close(self):
        self.awg.close()


def run():
    piano = Piano('USB0::62700::4355::SDG1XCAQ3R3321::0::INSTR')
    piano.close()
