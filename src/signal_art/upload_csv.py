import argparse
import logging
import time

import pandas

from awg import SignalGenerator
from oscilloscope import Oscilloscope


LOGGER = logging.getLogger(__file__)


def _read_signal(filename: str) -> bytes:
    LOGGER.info("- %s", filename)
    data = pandas.read_csv(filename)

    wave = ''
    for value in data.Volt:
        value = '{:04x}'.format(int(value * 8192))
        value = value[2:4] + value[:2]  # Big-endian to little-endian
        wave += value
    wave_bytes = bytearray.fromhex(wave)
    return bytes(wave_bytes).decode('latin1')


def _init_oscilloscope(addr):
    scope = Oscilloscope(addr)
    scope.write("XY_DISPLAY ON; ACQUIRE_WAY SAMPLING")
    time.sleep(0.2)
    scope.write("TIME_DIV 50US")
    scope.write("GRID_DISPLAY OFF")
    time.sleep(0.2)
    for channel in range(1, 3):
        scope.write(f"BANDWIDTH_LIMIT C{channel}, ON")
        scope.write(f"C{channel}:VOLT_DIV 0.05")
    scope.write("MENU OFF")


def populate_cli_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('--file-prefix',
                        default='drawing',
                        type=str,
                        help='Prefix for the CSV files (omit _x.csv)')


def run(args: argparse.Namespace):
    file_prefix = args.file_prefix

    awg = SignalGenerator(args.config['awg'].get('address'))
    awg.reset()
    LOGGER.info(awg.identify())
    time.sleep(3)

    LOGGER.info("Loading stereo signal: %s.", file_prefix)
    signal_x = _read_signal(f"{file_prefix}_x.csv")
    signal_y = _read_signal(f"{file_prefix}_y.csv")

    awg.set_output(1, False)
    awg.set_output(2, False)

    LOGGER.info("Uploading %s_x...", file_prefix)
    msg = f"C1:WVDT WVNM,{file_prefix}_x,FREQ,2000.0,AMPL,4.0,OFST,0.0,PHASE,0.0,WAVEDATA,{signal_x}"
    awg.write_raw(msg)
    awg.write(f"C1:ARWV NAME,{file_prefix}_x")
    time.sleep(5)

    LOGGER.info("Uploading %s_y...", file_prefix)
    msg = f"C2:WVDT WVNM,{file_prefix}_y,FREQ,2000.0,AMPL,4.0,OFST,0.0,PHASE,0.0,WAVEDATA,{signal_y}"
    awg.write_raw(msg)
    awg.write(f"C2:ARWV NAME,{file_prefix}_y")

    _init_oscilloscope(args.config['oscilloscope'].get('address'))

    awg.set_output(1, True)
    awg.set_output(2, True)
