#!/usr/bin/env python3
import argparse
import logging

import awg.awg_piano
import util.device_detection

COMMANDS = {
    'devices': util.device_detection.run,
    'piano': awg.awg_piano.run,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command',
                        choices=COMMANDS.keys(),
                        help='Mode of operation')
    parser.add_argument('--dry',
                        action='store_true',
                        help='Dry run without external devices')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    COMMANDS[args.command](args)


if __name__ == '__main__':
    main()
