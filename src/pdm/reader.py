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
                error = new_value['error']
                if error == 'overflow':
                    print(_format_for_human(error), flush=True)
                else:
                    LOGGER.error(new_value['error'])
                    break
            else:
                print(_format_for_human(new_value), flush=True)
            value = new_value

    multimeter.close()


def _format_for_human(reading):
    time = datetime.now().strftime('%H:%M:%S')
    if 'value' in reading:
        return f"{time}\t{reading['value']:g} {reading['unit']}"
    return f"{time}\t{reading}"
