#!/usr/bin/env python3
import argparse
import configparser
import logging

import awg.awg_piano
import oscilloscope.xy_demo
import pdm.reader
import signal_art.svg_to_signal
import signal_art.upload_csv
import util.device_detection

COMMANDS = {
    'devices': util.device_detection,
    'pdm': pdm.reader,
    'piano': awg.awg_piano,
    'svg2csv': signal_art.svg_to_signal,
    'xy-upload': signal_art.upload_csv,
    'xy-demo': oscilloscope.xy_demo,
}


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('command',
                        choices=COMMANDS.keys(),
                        help='Mode of operation')
    parser.add_argument('--config',
                        default='alab_config.ini',
                        type=str,
                        help='Configuration file name')
    parser.add_argument('--dry',
                        action='store_true',
                        help='Dry run without external devices')
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config)
    args.config = config

    logging.basicConfig(level=config['log']['level'])

    if args.dry:
        config.remove_option('awg', 'address')
        config.remove_option('oscilloscope', 'address')
        config.remove_option('pdm', 'address')

    COMMANDS[args.command].run(args)


if __name__ == '__main__':
    main()
