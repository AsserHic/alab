#!/usr/bin/env python3
from oscilloscope import Oscilloscope


def main():
    scope = Oscilloscope('192.168.2.3')
    scope.close()


if __name__ == '__main__':
    main()
