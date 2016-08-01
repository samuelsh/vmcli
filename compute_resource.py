"""
Compute Resource class

author: samuels
"""
from virtual_machine import VirtualMachine
from vmutils import VmUtils


class ComputeResource(object):
    def __init__(self, folder_name, name, si):
        self.name = name
        self.folder_name = folder_name
        self.si = si
        self._virtual_machines = []

        for vm in VmUtils.get_vms_by_compute_resource(self.folder_name, self.name, self.si):
            self._virtual_machines.append(VirtualMachine(self.folder_name, self.name, vm))

    @property
    def virtual_machines(self):
        return self._virtual_machines

    def insert(self, db):
        return db.insert_compute_resource_object(self)
