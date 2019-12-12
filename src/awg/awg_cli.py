#!/usr/bin/env python3
import logging

from signal_generator import SignalGenerator


def main():
    logging.basicConfig(level=logging.INFO)
    awg = SignalGenerator('USB0::62700::4355::SDG1XCAQ3R3321::0::INSTR')
    awg.write('C1:BSWV FRQ,2000')
    awg.close()


if __name__ == '__main__':
    main()
