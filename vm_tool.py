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
import textwrap

import time

import sys
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
from tools import cli, tasks, vm as vm_helper


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
    parser.add_argument('--action', choices=['list', 'poweron', 'poweroff', 'reboot', 'info'])
    parser.add_argument('-n', '--vmname', type=str, help="Some action are require name of specific VM.")
    args = parser.parse_args()
    return args


def _create_char_spinner():
    """Creates a generator yielding a char based spinner.
    """
    while True:
        for c in '|/-\\':
            yield c


_spinner = _create_char_spinner()


def spinner(label=''):
    """Prints label with a spinner.
    When called repeatedly from inside a loop this prints
    a one line CLI spinner.
    """
    sys.stdout.write("\r\t%s %s" % (label, _spinner.next()))
    sys.stdout.flush()


def answer_vm_question(virtual_machine):
    print("\n")
    choices = virtual_machine.runtime.question.choice.choiceInfo
    default_option = None
    if virtual_machine.runtime.question.choice.defaultIndex is not None:
        ii = virtual_machine.runtime.question.choice.defaultIndex
        default_option = choices[ii]
    choice = None
    while choice not in [o.key for o in choices]:
        print("VM power on is paused by this question:\n\n")
        print("\n".join(textwrap.wrap(
            virtual_machine.runtime.question.text, 60)))
        for option in choices:
            print("\t %s: %s " % (option.key, option.label))
        if default_option is not None:
            print("default (%s): %s\n" % (default_option.label,
                                          default_option.key))
        choice = raw_input("\nchoice number: ").strip()
        print("...")
    return choice


def reboot_vm(args, si):
    vm = si.content.searchIndex.FindByDnsName(None, args.vmname, True)
    print("Found: {0}".format(vm.name))
    print("The current powerState is: {0}".format(vm.runtime.powerState))
    task = vm.ResetVM_Task()
    tasks.wait_for_tasks(si, [task])
    print("its done.")


def poweron_vm(args, si):
    # search the whole inventory tree recursively... a brutish but effective tactic
    vm = si.content.searchIndex.FindByDnsName(None, args.vmname, True)
    if not isinstance(vm, vim.VirtualMachine):
        print("could not find a virtual machine with the name %s" % args.vmname)
        return 1

    print("Found VirtualMachine: %s Name: %s" % (vm, vm.name))
    print("VM State: %s" % vm.runtime.powerState)
    if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
        # using time.sleep we just wait until the power off action
        # is complete. Nothing fancy here.
        print("powering off...")
        task = vm.PowerOff()
        while task.info.state not in [vim.TaskInfo.State.success,
                                      vim.TaskInfo.State.error]:
            time.sleep(1)
        print("power is off.")

    # Sometimes we don't want a task to block execution completely
    # we may want to execute or handle concurrent events. In that case we can
    # poll our task repeatedly and also check for any run-time issues. This
    # code deals with a common problem, what to do if a VM question pops up
    # and how do you handle it in the API?
    print("powering on VM %s" % vm.name)
    if vm.runtime.powerState != vim.VirtualMachinePowerState.poweredOn:
        # now we get to work... calling the vSphere API generates a task...
        task = vm.PowerOn()
        answers = {}
        while task.info.state not in [vim.TaskInfo.State.success,
                                      vim.TaskInfo.State.error]:
            # we'll check for a question, if we find one, handle it,
            # Note: question is an optional attribute and this is how pyVmomi
            # handles optional attributes. They are marked as None.
            if vm.runtime.question is not None:
                question_id = vm.runtime.question.id
                if question_id not in answers.keys():
                    answers[question_id] = answer_vm_question(vm)
                    vm.AnswerVM(question_id, answers[question_id])

            # create a spinning cursor so people don't kill the script...
            spinner(task.info.state)

        if task.info.state == vim.TaskInfo.State.error:
            # some vSphere errors only come with their class and no other message
            print("error type: %s" % task.info.error.__class__.__name__)
            print("found cause: %s" % task.info.error.faultCause)
            for fault_msg in task.info.error.faultMessage:
                print(fault_msg.key)
                print(fault_msg.message)
            return 1


def do_vm_action(args, si):
    if args.action == "list":
        content = si.RetrieveContent()
        for child in content.rootFolder.childEntity:
            if hasattr(child, 'vmFolder'):
                datacenter = child
                vm_folder = datacenter.vmFolder
                vm_list = vm_folder.childEntity
                for vm in vm_list:
                    vm_helper.print_vm_info(vm)

    elif args.action == "info":
        if not args.vmname:
            raise RuntimeError("VM name not specified")
        vm = si.content.searchIndex.FindByDnsName(None, args.vmname, True)
        if vm is None:
            raise RuntimeError('VM %s not found' % args.vmname)
        vm_helper.print_vm_info(vm)

    elif args.action == "reboot":
        reboot_vm(args, si)

    elif args.action == "poweroff" or args.action == "poweron":
        poweron_vm(args, si)


def main():
    """
   """

    args = get_args()
    if args.password:
        password = args.password
    else:
        password = getpass.getpass(prompt='Enter password for host %s and '
                                          'user %s: ' % (args.host, args.user))

    si = SmartConnect(host=args.host,
                      user=args.user,
                      pwd=password)
    if not si:
        print("Could not connect to the specified host using specified "
              "username and password")
        return -1

    atexit.register(Disconnect, si)

    do_vm_action(args, si)

    return 0


# Start program
if __name__ == "__main__":
    main()
