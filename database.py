import sqlite3

__author__ = 'samuels'

TEST_SUITE_DB_PATH = "vms.db"

VM_HOST_FOLDER_TABLE_NAME = "vmhost_folder_table"
VM_COMPUTE_RESOURCE_TABLE_NAME = "compute_resource_table"
VMS_TABLE_NAME = "vms_table"


class DataBase:
    def __init__(self, logger):
        self._logger = logger
        self._db_connection = sqlite3.connect(TEST_SUITE_DB_PATH)
        self._cursor = self._db_connection.cursor()

        self._cursor.execute("DROP TABLE IF EXISTS %s" % VM_HOST_FOLDER_TABLE_NAME)
        self._cursor.execute("DROP TABLE IF EXISTS %s" % VM_COMPUTE_RESOURCE_TABLE_NAME)
        self._cursor.execute("DROP TABLE IF EXISTS %s" % VMS_TABLE_NAME)

        self._cursor.execute('''CREATE TABLE IF NOT EXISTS %s
             (
                id                  INTEGER PRIMARY KEY NOT NULL,
                name                TEXT
                )''' % VM_HOST_FOLDER_TABLE_NAME)

        self._cursor.execute('''CREATE TABLE IF NOT EXISTS %s
             (
                id              INTEGER PRIMARY KEY NOT NULL,
                name            TEXT,
                folder_name     TEXT,
                FOREIGN KEY (name) REFERENCES %s (folder_name)
                )''' % (VM_COMPUTE_RESOURCE_TABLE_NAME, VM_HOST_FOLDER_TABLE_NAME))

        self._cursor.execute('''CREATE TABLE IF NOT EXISTS %s
             (
                id              INTEGER PRIMARY KEY NOT NULL,
                folder_name     TEXT,
                cmp_res_name    TEXT,
                name            TEXT,
                path            TEXT,
                guest           TEXT,
                uuid            TEXT,
                cpunum          INTEGER,
                ram             text,
                state           text,
                ip              text,
                FOREIGN KEY(cmp_res_name) REFERENCES %s(name)
                )''' % (VMS_TABLE_NAME, VM_COMPUTE_RESOURCE_TABLE_NAME))

    def insert_host_folder_object(self, host_folder):
        """:type host_folder: VMHostFolder"""
        try:
            self._cursor.execute('insert into %s values (?)' % VM_HOST_FOLDER_TABLE_NAME,
                                 (host_folder.name,))
        except Exception as err:
            self._logger.exception('Table %s, Insert Query Failed: %s\n Error: %s' % (
                VM_HOST_FOLDER_TABLE_NAME, (host_folder.name,),
                str(err)))
            raise err

    def insert_compute_resource_object(self, compute_resource):
        """:type compute_resource: ComputeResource"""
        try:
            self._cursor.execute('insert into %s values (?,?)' % VM_COMPUTE_RESOURCE_TABLE_NAME,
                                 (compute_resource.name, compute_resource.folder_name,))
        except Exception as err:
            self._logger.exception('Table %s, Insert Query Failed: %s\n Error: %s' % (
                VM_COMPUTE_RESOURCE_TABLE_NAME,
                (compute_resource.name, compute_resource.folder_name),
                str(err)))
            raise err

    def insert_vms_object(self, virtual_machine):
        """:type virtual_machine: VirtualMachine"""
        try:
            self._cursor.execute('insert into %s values (?,?,?,?,?,?,?,?,?,?)' % VMS_TABLE_NAME,
                                 (
                                     virtual_machine.foder_name, virtual_machine.cmp_res_name,
                                     virtual_machine.name,
                                     virtual_machine.path, virtual_machine.guest,
                                     virtual_machine.UUID, virtual_machine.num_of_cpus, virtual_machine.ram,
                                     virtual_machine.state, virtual_machine.ip,))
        except Exception as err:
            self._logger.exception('Table %s, Insert Query Failed: %s\n Error: %s' % (
                VMS_TABLE_NAME,
                (virtual_machine.foder_name, virtual_machine.cmp_res_name, virtual_machine.name, virtual_machine.path,
                 virtual_machine.guest,
                 virtual_machine.UUID, virtual_machine.num_of_cpus, virtual_machine.ram,
                 virtual_machine.state, virtual_machine.ip),
                str(err)))
            raise err

    def insert(self, item):
        return item.insert(self)

    def __del__(self):
        self._logger.info("Closing DB connection...")
        self._db_connection.close()
