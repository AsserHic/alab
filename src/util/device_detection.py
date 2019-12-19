import argparse
import logging

import visa

LOGGER = logging.getLogger(__file__)


def list_devices():
    rm = visa.ResourceManager('@py')

    return rm.list_resources()


def run(args: argparse.Namespace):
    for i, dev in enumerate(list_devices()):
        LOGGER.info("%s: %s", i, dev)
