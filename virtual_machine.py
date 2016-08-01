"""
Virtual Machine class

author: samuels
"""


class VirtualMachine(object):
    def __init__(self, folder_name, cmp_res_name, vm):
        """
        :type vm: tuple
        """
        self.folder_name = folder_name
        self.cmp_res_name = cmp_res_name
        (self.name, self.path, self.guest, self.UUID, self.num_of_cpus, self.ram, self.state, self.ip) = vm

    def insert(self, db):
        return db.insert_virtual_machine_object(self)
