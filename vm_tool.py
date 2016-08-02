#!/usr/bin/env python
# VMware vSphere Python SDK
# Copyright (c) 2008-2015 VMware, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Python program for listing the vms on an ESX / vCenter host
"""

from __future__ import print_function

import argparse
import atexit
import getpass

from pyVim.connect import SmartConnect, Disconnect

from database import DataBase
from logger import Logger
from vmhostfolder import VmHostFolder
from vmutils import VmUtils


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
    parser.add_argument('--action',
                        choices=['list', 'poweron', 'poweroff', 'reboot', 'info', 'folder', 'listfolders', 'byfolder'])
    parser.add_argument('-n', '--vmname', type=str, help="")
    parser.add_argument('-f', '--fname', type=str, help="")
    parser.add_argument('--dump2db', action='store_true')
    args = parser.parse_args()
    return args


def do_vm_action(logger, args, vm_folders, si, db=None):
    """
    :param logger
    :type logger: logging
    :param args:
    :param vm_folders:
    :type vm_folders: VmHostFolder[]
    :param si:
    :param db:
    :type db: DataBase
    :return:
    """
    if args.action == "list":
        VmUtils.list_all_vms(si)
    elif args.action == "info":
        if not args.vmname:
            raise RuntimeError("VM name not specified")
        VmUtils.print_vm_info(args, si)
    elif args.action == "reboot":
        VmUtils.reboot_vm(args, si)
    elif args.action == "poweroff" or args.action == "poweron":
        VmUtils.poweron_vm(args, si)
    elif args.action == "folder":
        VmUtils.print_vm_folder(args, si)
    elif args.action == "listfolders":
        VmUtils.print_all_folders(si)
    elif args.action == "byfolder":
        if not args.fname:
            raise RuntimeError("VM folder not specified")
        VmUtils.print_vms_by_folder(args, si)

    if args.dump2db:
        if db is None:
            raise RuntimeError("DB isn't initialised")
        logger.info("Scanning VM folders. Can take some time....")
        for folder in VmUtils.get_all_folders(si):
            vm_folders.append(VmHostFolder(folder, si))
        logger.debug("Found folders: {}".format(len(vm_folders)))
        logger.info("Dumping to DB...")
        for folder in vm_folders:
            folder.insert(db)
            logger.debug("Folder {0} inserted to DB".format(folder.name))
            for cmp_resource in folder.compute_resources:
                cmp_resource.insert(db)
                logger.debug("Computer Resource {0} inserted to DB".format(cmp_resource.name))
                for vm in cmp_resource.virtual_machines:
                    vm.insert(db)
                    logger.debug("VM {0} inserted to DB".format(vm.name))
        logger.info("Done dumping to DB")


def main():
    """
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

    do_vm_action(logger, args, vm_folders, si, data_base)

    return 0


# Start program
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
