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
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    COMMANDS[args.command]()


if __name__ == '__main__':
    main()