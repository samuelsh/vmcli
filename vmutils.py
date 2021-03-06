"""

"""
import socket
import sys
import textwrap

import time

from colorama import Fore
from colorama import init

from tools import tasks, vm as vm_helper
from pyVmomi import vim

try:
    from __builtin__ import input  # for Python 3 compatibility
except ImportError:
    from builtins import input

TREE_LEAF = "\xe2\x94\x9c"
TREE_LEAF_END = "\xe2\x94\x94"
TREE_LEVEL = "\xE2\x94\x80"
TREE_PIPE = "\xe2\x94\x82"

TREE_ENTRY = TREE_LEAF + TREE_LEVEL + TREE_LEVEL
TREE_ENTRY_END = TREE_LEAF_END + TREE_LEVEL + TREE_LEVEL
TREE_PADDING = TREE_PIPE + " " * 3
TREE_PADDING_EMPTY = " " * 4


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
        choice = input("\nchoice number: ").strip()
        print("...")
    return choice


def print_vm_info(args, si):
    vm = si.content.searchIndex.FindByIp(None, get_ip_by_host(args.vmname), True)
    if vm is None:
        raise RuntimeError('VM %s not found' % args.vmname)
    vm_helper.print_vm_info(vm)


def list_all_vms(si):
    content = si.RetrieveContent()
    for child in content.rootFolder.childEntity:
        if hasattr(child, 'vmFolder'):
            datacenter = child
            vm_folder = datacenter.hostFolder
            vm_list = vm_folder.childEntity
            for vm in vm_list:
                vm_helper.print_vm_info(vm)


def print_vm_folder(args, si):
    vm = si.content.searchIndex.FindByDnsName(None, args.vmname, True)
    if vm is None:
        raise RuntimeError('VM %s not found' % args.vmname)
    print("Parent Folder: %s" % vm.parent.name)


def print_folder(folder, level=0, folders_only=False, args=None):
    child_folders = None
    try:
        if hasattr(folder, 'childEntity'):  # This is generic folder
            child_folders = folder.childEntity
        elif hasattr(folder, 'vmFolder'):  # This is Datacenter
            print("{0}".format(folder.vmFolder.name))
            return
        if folders_only:
            child_folders = [f for f in child_folders if not hasattr(f, 'capability')]  # removing VMs from list
        for i, f in enumerate(child_folders):
            print("{0:20}{1:20}{2}".format(f.name, get_obj_type(f), get_vm_power_state(f)))
            if hasattr(f, 'childEntity'):
                print_folder(f, level + 1)  # go deeper it's a folder
    except AttributeError as att_err:
        print(att_err)
        pass


def get_obj_type(folder):
    if not is_folder(folder):
        return "VM"
    return "Folder"


def get_vm_power_state(vm):
    try:
        return Fore.GREEN + vm.runtime.powerState + Fore.RESET
    except AttributeError:
        return ""


def is_folder(folder):
    if not hasattr(folder, 'childEntity') and not hasattr(folder, 'vmFolder'):
        return False
    return True


def get_folder_by_name(start_folder, name):
    child_folders = None
    if hasattr(start_folder, 'childEntity'):  # This is generic folder
        child_folders = start_folder.childEntity
    elif hasattr(start_folder, 'vmFolder'):  # This is Datacenter
        if start_folder.vmFolder.name == name:
            return start_folder.vmFolder
        return None
    return next((f for f in child_folders if f.name == name and is_folder(f)), None)  # stop on 1st match


def print_all_folders(args, si):
    content = si.RetrieveContent()
    for child in content.rootFolder.childEntity:
        if hasattr(child, 'vmFolder'):
            print("---------------- DataCenter: %s ------------------" % child.name)
            datacenter = child
            level = 1
            if args.view == "hosts":
                print('Hosts & Cluster')
                vm_folders = datacenter.hostFolder
                for folder in vm_folders.childEntity:
                    # if hasattr(folder, 'childType'):  # if childType isn't exist, its a VM
                    #     print("{0} {1}".format('-' * level, folder.name))
                    print_folder(folder, level)
            if args.view == "vms":
                print('Vms & Templates')
                vm_folders = datacenter.vmFolder
                try:
                    # for folder in vm_folders.childEntity:
                    # if hasattr(folder, 'childType'):  # if childType isn't exist, its a VM
                    #     print("{0} {1}".format('-' * level, folder.name))
                    print_folder(vm_folders, level, args.folders_only)
                except AttributeError:
                    pass


def print_vm_tree_vms(args, si):
    content = si.RetrieveContent()
    for child in content.rootFolder.childEntity:
        if hasattr(child, 'vmFolder'):
            datacenter = child
            level = 1
            if args.view == "hosts":
                print("{0}".format(child.name))
                vm_folders = datacenter.hostFolder
                for folder in vm_folders.childEntity:
                    # if hasattr(folder, 'childType'):  # if childType isn't exist, its a VM
                    #     print("{0} {1}".format('-' * level, folder.name))
                    print_folder(folder, level)
            if args.view == "vms":
                print("{0}".format(child.name))
                vm_folders = datacenter.vmFolder
                try:
                    print_recursive_tree(vm_folders, 0, args.folders_only)
                except AttributeError:
                    pass


def print_vm_tree_hosts(args, si):
    content = si.RetrieveContent()
    for child in content.rootFolder.childEntity:
        if hasattr(child, 'vmFolder'):
            print("---------------- DataCenter: %s ------------------" % child.name)
            datacenter = child
            level = 1
            if args.view == "hosts":
                print('Hosts & Cluster')
                vm_folders = datacenter.hostFolder
                for folder in vm_folders.childEntity:
                    # if hasattr(folder, 'childType'):  # if childType isn't exist, its a VM
                    #     print("{0} {1}".format('-' * level, folder.name))
                    print_folder(folder, level)
            if args.view == "vms":
                print('Vms & Templates')
                vm_folders = datacenter.vmFolder
                try:
                    # for folder in vm_folders.childEntity:
                    # if hasattr(folder, 'childType'):  # if childType isn't exist, its a VM
                    #     print("{0} {1}".format('-' * level, folder.name))
                    print_folder(vm_folders, level)
                except AttributeError:
                    pass


def get_all_folders(si):
    flist = []
    content = si.RetrieveContent()
    for child in content.rootFolder.childEntity:
        if hasattr(child, 'vmFolder'):
            datacenter = child
            vm_folders = datacenter.hostFolder
            for folder in vm_folders.childEntity:
                flist.append(folder.name)
    return flist


def get_compute_resources_by_folder(folder_name, si):
    content = si.RetrieveContent()
    cres_list = []
    for child in content.rootFolder.childEntity:
        if hasattr(child, 'vmFolder'):  # is object a datacenter ?
            datacenter = child
            vm_folders = datacenter.hostFolder
            for folder in vm_folders.childEntity:
                if folder.name == folder_name:
                    resources = folder.childEntity
                    for res in resources:
                        cres_list.append(res.name)
    return cres_list


def get_vms_by_compute_resource(folder_name, cmp_res_name, si):
    content = si.RetrieveContent()
    vms_list = []
    for child in content.rootFolder.childEntity:
        if hasattr(child, 'vmFolder'):  # is object a datacenter ?
            datacenter = child
            vm_folders = datacenter.hostFolder
            for folder in vm_folders.childEntity:
                if folder.name == folder_name:
                    resources = folder.childEntity
                    for res in resources:
                        if res.name == cmp_res_name:
                            for vm in res.resourcePool.vm:
                                summary = vm.summary
                                vms_list.append(
                                    (summary.config.name, summary.config.vmPathName, summary.config.guestFullName,
                                     summary.config.instanceUuid, summary.config.numCpu,
                                     summary.config.memorySizeMB,
                                     summary.runtime.powerState, summary.guest.ipAddress))
    return vms_list


def print_vms_by_folder(args, si):
    content = si.RetrieveContent()
    for child in content.rootFolder.childEntity:
        if hasattr(child, 'vmFolder'):  # is object a datacenter ?
            datacenter = child
            if args.view == "hosts":
                vm_folders = datacenter.hostFolder
                for folder in vm_folders.childEntity:
                    print("{0} -- {1}".format(type(folder), folder.name))
                    if folder.name == args.fname:
                        resources = folder.childEntity
                        for res in resources:
                            print("Compute Resource: %s" % res.name)
                            for vm in res.resourcePool.vm:
                                vm_helper.print_vm_info(vm)
            if args.view == "vms":
                vm_folders = datacenter.vmFolder
                for folder in vm_folders.childEntity:
                    print("{0} -- {1}".format(type(folder), folder.name))

        else:
            print("Folder %s not found" % args.fname)


def print_tree(si):
    pass


def print_recursive_tree(folder, level=0, folders_only=False):
    try:
        child_folders = folder.childEntity
        tree_padding = TREE_PADDING
        if folders_only:
            child_folders = [f for f in child_folders if not hasattr(f, 'capability')]  # removing VMs from list
        for i, f in enumerate(child_folders):
            if i >= len(child_folders) - 1:
                tree_entry = TREE_ENTRY_END
            else:
                tree_entry = TREE_ENTRY
            print("{0}{1} {2} ({3} of {4})".format(tree_padding * level, tree_entry, f.name, i + 1,
                                                   len(child_folders)))
            if hasattr(f, 'childEntity'):
                print_recursive_tree(f, level + 1, folders_only)  # go deeper it's a folder
    except AttributeError as att_err:
        print(att_err)
        pass


def dump2db(args, si, db):
    pass


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

    if args.action == "poweroff" and vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOff:
        print("VM %s is already Powered Off." % vm.name)
        return 0

    if args.action == "poweron" and vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
        print("VM %s is already Powered On." % vm.name)
        return 0

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
        return 0

    # Sometimes we don't want a task to block execution completely
    # we may want to execute or handle concurrent events. In that case we can
    # poll our task repeatedly and also check for any run-time issues. This
    # code deals with a common problem, what to do if a VM question pops up
    # and how do you handle it in the API?
    if vm.runtime.powerState != vim.VirtualMachinePowerState.poweredOn:
        # now we get to work... calling the vSphere API generates a task...
        print("powering on VM %s" % vm.name)
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
    return 0


def get_ip_by_host(hostname):
    """
    :type hostname: str
    :rtype: str
    """
    return socket.gethostbyname(hostname)


def get_host_by_ip(ip):
    """
    :type ip: str
    :rtype: str
    """
    return socket.gethostbyname(ip)
