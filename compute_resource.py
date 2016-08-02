"""
Compute Resource class

author: samuels
"""
from virtual_machine import VirtualMachine
from vmutils import VmUtils


class ComputeResource(object):
    def __init__(self, folder_name, name, si):
        self._name = name
        self._folder_name = folder_name
        self._si = si
        self._virtual_machines = []

        for vm in VmUtils.get_vms_by_compute_resource(self._folder_name, self._name, self._si):
            self._virtual_machines.append(VirtualMachine(self._folder_name, self._name, vm))

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._folder_name

    @property
    def virtual_machines(self):
        return self._virtual_machines

    def insert(self, db):
        return db.insert_compute_resource_object(self)
