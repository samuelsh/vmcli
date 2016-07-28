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
                id                  INTEGER PRIMARY KEY,
                name                TEXT,
                )''' % VM_HOST_FOLDER_TABLE_NAME)

        self._cursor.execute('''CREATE TABLE IF NOT EXISTS %s
             (
                id              INTEGER PRIMARY KEY,
                name            TEXT,
                FOREIGN KEY (id) REFERENCES %s (id)
                )''' % (VM_COMPUTE_RESOURCE_TABLE_NAME, VM_HOST_FOLDER_TABLE_NAME))

        self._cursor.execute('''CREATE TABLE IF NOT EXISTS %s
             (
                id              INTEGER PRIMARY KEY,
                name            TEXT,
                path            TEXT,
                guest           TEXT,
                uuid            TEXT,
                cpunum          INTEGER,
                ram             text,
                state           text,
                ip              text,
                FOREIGN KEY(id) REFERENCES %s(id)
                )''' % (VMS_TABLE_NAME, VM_COMPUTE_RESOURCE_TABLE_NAME))

    def _insert_rack_folder_object(self, file_object):
        """:type file_object: DedupedFluidFSFile"""
        try:
            self._cursor.execute('insert into %s values (?,?,?,?,?)' % VM_HOST_FOLDER_TABLE_NAME,
                                 (file_object.dsid, file_object.timestamp,
                                  file_object.get_file_path_cluster(),
                                  file_object.file_size, file_object.fsid,))
        except Exception as err:
            self._logger.exception('Table %s, Insert Query Failed: %s\n Error: %s' % (
                VM_HOST_FOLDER_TABLE_NAME, (file_object.dsid, file_object.timestamp,
                                         file_object.get_file_path_cluster(),
                                         file_object.file_size, file_object.fsid),
                str(err)))
            raise err

    def _insert_compute_resource_object(self, block_map_object):
        """:type block_map_object: OSDBlockMap"""
        try:
            self._cursor.execute('insert into %s values (?,?,?)' % VM_COMPUTE_RESOURCE_TABLE_NAME,
                                 (block_map_object.bm_scid, block_map_object.bm_node, block_map_object.dsid,))
        except Exception as err:
            self._logger.exception('Table %s, Insert Query Failed: %s\n Error: %s' % (
                VM_COMPUTE_RESOURCE_TABLE_NAME,
                (block_map_object.bm_scid, block_map_object.bm_node, block_map_object.dsid),
                str(err)))
            raise err

    def _insert_vms_object(self, data_store_object):
        """:type data_store_object: OSDDataStore"""
        try:
            self._cursor.execute('insert into %s values (?,?,?)' % VMS_TABLE_NAME,
                                 (data_store_object.ds_scid, data_store_object.ds_node, data_store_object.bm_scid,))
        except Exception as err:
            self._logger.exception('Table %s, Insert Query Failed: %s\n Error: %s' % (
                VMS_TABLE_NAME,
                (data_store_object.ds_scid, data_store_object.ds_node, data_store_object.bm_scid),
                str(err)))
            raise err

    def insert(self, fluidfs_object):
        self._logger.info("inserting %s object", fluidfs_object.__class__.__name__)
        if isinstance(fluidfs_object, DedupedFluidFSFile):
            self._insert_file_object(fluidfs_object)
        elif isinstance(fluidfs_object, OSDBlockMap):
            self._insert_block_map_object(fluidfs_object)
        elif isinstance(fluidfs_object, OSDDataStore):
            self._insert_data_store_object(fluidfs_object)
        else:
            self._logger.error("Insert Failed. Bad object type %s" % type(fluidfs_object))
            raise Exception
        self._db_connection.commit()

    def __del__(self):
        self._logger.info("Closing DB connection...")
        self._db_connection.close()
