#!/usr/bin/python
"""
vCli - cli tool to manage VMWare VMs
"""
import argparse
import atexit
import getpass
import sys
import traceback

from pyVim.connect import SmartConnect, Disconnect

from database import DataBase
from logger import Logger
from vmshell import VMShell


def get_args():
    """
    Supports the command-line arguments listed below.
    """

    parser = argparse.ArgumentParser(
        description='Process args for retrieving all the Virtual Machines')
    parser.add_argument('-s', '--host', required=True, action='store',
                        help='Remote host to connect to')
    parser.add_argument('-o', '--port', type=int, default=443, action='store',
                        help='Port to connect on')
    parser.add_argument('-u', '--user', required=True, action='store',
                        help='User name to use when connecting to host')
    parser.add_argument('-p', '--password', required=False, action='store',
                        help='Password to use when connecting to host')
    parser.add_argument('--dump2db', action='store_true')
    args = parser.parse_args()
    return args


def main():
    """

    :return:
    """
    data_base = None
    vm_folders = []
    args = get_args()
    logger = Logger().logger
    logger.debug("Logger Initialized %s" % logger)
    if args.dump2db:
        data_base = DataBase(logger)
        logger.info("SQLite DB initialized %s" % data_base)

    if args.password:
        password = args.password
    else:
        password = getpass.getpass(prompt='Enter password for host %s and '
                                          'user %s: ' % (args.host, args.user))

    si = SmartConnect(host=args.host,
                      user=args.user,
                      pwd=password)
    if not si:
        logger.error("Could not connect to the specified host using specified "
                     "username and password")
        return -1

    atexit.register(Disconnect, si)

    VMShell(si, args).cmdloop()

    return 0


# Start program
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
