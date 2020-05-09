import argparse
import logging

from .pdm300c2 import PDM300

LOGGER = logging.getLogger(__file__)


def run(args: argparse.Namespace):
    port = args.config['pdm'].get('port')
    LOGGER.info("Connecting a multimeter at %s...", port)
    multimeter = PDM300(port)

    value = multimeter.read()
    print(value)

    multimeter.close()
