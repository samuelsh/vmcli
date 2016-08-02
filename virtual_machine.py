"""
Virtual Machine class

author: samuels
"""


class VirtualMachine(object):
    def __init__(self, folder_name, cmp_res_name, vm):
        """
        :type vm: tuple
        """
        self._folder_name = folder_name
        self._cmp_res_name = cmp_res_name
        (self._name, self._path, self._guest, self._UUID, self._num_of_cpus, self._ram, self._state, self._ip) = vm

    @property
    def folder_name(self):
        return self._folder_name

    @property
    def cmp_res_name(self):
        return self._cmp_res_name

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path

    @property
    def guest(self):
        return self._guest

    @property
    def UUID(self):
        return self._UUID

    @property
    def num_of_cpus(self):
        return self._num_of_cpus

    @property
    def ram(self):
        return self._ram

    @property
    def state(self):
        return self._state

    @property
    def ip(self):
        return self._ip

    def insert(self, db):
        return db.insert_virtual_machine_object(self)
