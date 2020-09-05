import argparse
import logging

import pandas

from awg import SignalGenerator


LOGGER = logging.getLogger(__file__)


def _read_signal(filename: str):
    LOGGER.info("- %s", filename)
    df = pandas.read_csv(filename, sep="\t")

    wave = ''
    for value in df.x:
        value = '{:04x}'.format(int(value * 65536))
        wave += value
    wave = bytearray.fromhex(wave[:-1])
    return bytes(wave)


def run(args: argparse.Namespace):
    file_prefix = 'drawing'

    awg = SignalGenerator(args.config['awg'].get('address'))
    awg.reset()
    print(awg.identify())

    LOGGER.info("Uploading stereo signal: %s.", file_prefix)
    signal_x = _read_signal(f"{file_prefix}_x.csv")
    signal_y = _read_signal(f"{file_prefix}_y.csv")

    #awg.write(f"C1:WVDT WVNM,wave1,FREQ,2000.0,AMPL,4.0,OFST,0.0,PHASE,0.0,WAVEDATA,{signal_x}" )
    #awg.write("C1:ARWV NAME,wave1")

    awg.close()