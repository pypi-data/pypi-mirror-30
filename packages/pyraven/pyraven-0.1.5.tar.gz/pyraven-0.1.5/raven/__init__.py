#!/usr/bin/env python

from . import raven
from . import _version
import argparse


def main():
    parser = argparse.ArgumentParser(prog="raven",
                                     description="Interrogate the RAVEn USB IHD")
    parser.add_argument('--port', '-p',
                        help='Serial port of the USB stick [/dev/ttyUSB0]',
                        default="/dev/ttyUSB0")
    parser.add_argument('--limit', '-l',
                        help='Count of events to consume before stopping [1000]',
                        default=1000)
    parser.add_argument('--version', '-V',
                        action='version',
                        version='%(prog)s {version}'.format(version=_version.__version__))
    args = parser.parse_args()

    raven_usb = raven.Raven(vars(args)['port'])
    print(raven_usb.get_connection_status())
    print(raven_usb.get_summation_delivered())

    # just wait for a while, because the scheduler inside the stick delivers
    # instantaneous demand automatically
    limit = int(vars(args)['limit']) or -1
    while limit < 0 or limit > 0:
        print(raven_usb.long_poll_result())
        if limit > 0:
            limit -= 1


if __name__ == "__main__":
    main()
