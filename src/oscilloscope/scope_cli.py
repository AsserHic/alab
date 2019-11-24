#!/usr/bin/env python3
import logging

from oscilloscope import Oscilloscope


def main():
    logging.basicConfig(level=logging.INFO)
    scope = Oscilloscope('TCPIP::192.168.2.3::5025::SOCKET')
    #scope.reset()
    #scope.auto_setup()
    print(scope.query('ALL_STATUS?'))
    scope.close()


if __name__ == '__main__':
    main()
