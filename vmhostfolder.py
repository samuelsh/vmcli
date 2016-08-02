"""
VM Rack class
author: samuels
"""
from compute_resource import ComputeResource
from vmutils import VmUtils


class VmHostFolder(object):
    def __init__(self, name, si):
        """
        :param name:
        :param db:
        :type db: DataBase
        """
        self._name = name
        self._si = si
        self._compute_resources = []

        for res in VmUtils.get_compute_resources_by_folder(self.name, self._si):
            self._compute_resources.append(ComputeResource(self.name, res, self._si))

    @property
    def name(self):
        return self._name

    @property
    def compute_resources(self):
        return self._compute_resources

    def insert(self, db):
        return db.insert_host_folder_object(self)
