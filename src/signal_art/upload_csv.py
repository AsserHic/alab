import argparse
import logging

import pandas


LOGGER = logging.getLogger(__file__)


def _upload_signal(filename: str):
    LOGGER.info("- %s", filename)
    df = pandas.read_csv(filename, sep="\t")

    for value in df.x:
        value = hex(int(value * 65536))
        value = value.zfill(4)
        print(value)


def run(args: argparse.Namespace):
    file_prefix = 'drawing'
    LOGGER.info("Uploading stereo signal: %s.", file_prefix)

    _upload_signal(f"{file_prefix}_x.csv")
    _upload_signal(f"{file_prefix}_y.csv")
