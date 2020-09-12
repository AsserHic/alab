import argparse
import logging


LOGGER = logging.getLogger(__file__)


def run(args: argparse.Namespace):
    LOGGER.info('Hello!')
