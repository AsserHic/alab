import argparse
from datetime import datetime
import logging

from .pdm300c2 import PDM300

LOGGER = logging.getLogger(__file__)


def run(args: argparse.Namespace):
    port = args.config['pdm'].get('address')
    multimeter = PDM300(port)

    mode = None
    value = None
    while True:
        new_value = multimeter.read()
        if new_value != value:
            if new_value.get('mode') != mode:
                mode = new_value.get('mode', 'unknown')
                LOGGER.info("Multimeter mode is %s.", mode)

            if 'error' in new_value:
                LOGGER.error(new_value['error'])
            else:
                print(_format_for_human(new_value))
            value = new_value

    multimeter.close()


def _format_for_human(reading):
    if 'value' in reading:
        time = datetime.now().strftime('%H:%M:%S')
        return f"{time}\t{reading['value']:g} {reading['unit']}"
    return reading
