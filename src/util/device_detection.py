#!/usr/bin/env python3
import visa


def main():
    rm = visa.ResourceManager('@py')
    print(rm.list_resources())


if __name__ == '__main__':
    main()
