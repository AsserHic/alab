import argparse
import logging

import pandas


LOGGER = logging.getLogger(__file__)


def _upload_signal(filename: str):
    LOGGER.info("- %s", filename)
    df = pandas.read_csv(filename, sep="\t")

    wave = ''
    for value in df.x:
        value = '{:04x}'.format(int(value * 65536))
        wave += value
    wave = bytearray.fromhex(wave[:-1])
    print(wave)  # https://siglentna.com/USA_website_2014/Documents/Program_Material/SDG_ProgrammingGuide_PG_E03B.pdf


def run(args: argparse.Namespace):
    file_prefix = 'drawing'
    LOGGER.info("Uploading stereo signal: %s.", file_prefix)

    _upload_signal(f"{file_prefix}_x.csv")
    _upload_signal(f"{file_prefix}_y.csv")
