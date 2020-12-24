import argparse
import logging
import time

import pandas

from awg import SignalGenerator


LOGGER = logging.getLogger(__file__)


def _read_signal(filename: str):
    LOGGER.info("- %s", filename)
    data = pandas.read_csv(filename)

    wave = ''
    for value in data.Volt:
        value = '{:04x}'.format(int(value * 65536))
        wave += value
    wave = bytearray.fromhex(wave[:-1])
    return bytes(wave)


def run(args: argparse.Namespace):
    file_prefix = 'drawing'

    awg = SignalGenerator(args.config['awg'].get('address'))
    awg.reset()
    LOGGER.info(awg.identify())
    time.sleep(3)

    LOGGER.info("Uploading stereo signal: %s.", file_prefix)
    signal_x = _read_signal(f"{file_prefix}_x.csv")
    signal_y = _read_signal(f"{file_prefix}_y.csv")

    msg = f"C1:WVDT WVNM,{file_prefix}_x,FREQ,2000.0,AMPL,4.0,OFST,0.0,PHASE,0.0,WAVEDATA,{signal_x}"
    awg.write_raw(msg)
    awg.write("C1:ARWV NAME,{file_prefix}_x")
    time.sleep(5)

    msg = f"C2:WVDT WVNM,{file_prefix}_y,FREQ,2000.0,AMPL,4.0,OFST,0.0,PHASE,0.0,WAVEDATA,{signal_y}"
    awg.write_raw(msg)
    awg.write("C2:ARWV NAME,{file_prefix}_y")

    awg.close()
