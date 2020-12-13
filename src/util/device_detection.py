import argparse
import logging

import pyvisa

LOGGER = logging.getLogger(__file__)


def list_devices():
    rm = pyvisa.ResourceManager('@py')

    return rm.list_resources()


def run(args: argparse.Namespace):
    names = _device_names(args.config)
    for i, dev in enumerate(list_devices()):
        LOGGER.info("%s: %s (%s)",
                    i, dev, names.get(dev, 'unknown'))


def _device_names(cfg):
    names = {}
    for section in cfg:
        if 'address' in cfg[section]:
            names[cfg[section]['address']] = section
    return names
