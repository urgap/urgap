import unittest

from copy import deepcopy

from urgap.umeta.io._base import UMetaIOBase


class TestUMetaIOBase(unittest.TestCase):
    def setUp(self):
        self.obj = UMetaIOBase()

    def test_deepcopy(self):
        self.obj.attr1 = "value1"
        self.obj.attr2 = [1, 2, 3]
        self.obj._private = "should_not_copy"

        obj_copy = deepcopy(self.obj)

        self.assertEqual(obj_copy.attr1, "value1")
        self.assertEqual(obj_copy.attr2, [1, 2, 3])
        self.assertFalse(hasattr(obj_copy, "_private"))
        self.assertIsNot(self.obj, obj_copy)
        self.assertIsNot(self.obj.attr2, obj_copy.attr2)

    def test_load_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.obj.load()

    def test_save_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.obj.save()

    def test_find_wid_members_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.obj.find_wid_members("some_wid")

    def test_find_pac_ids_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.obj.find_pac_ids("some_object")

    def test_find_pac_ids_of_producers_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.obj.find_pac_ids_of_producers("some_object")

    def test_find_pac_ids_of_consumers_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.obj.find_pac_ids_of_consumers("some_object")

    def test_retrieve_interface_statistics_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.obj.retrieve_interface_statistics()

    def test_find_last_processed_files_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.obj.find_last_processed_files()

    def test_find_pac_id_details_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.obj.find_pac_id_details("some_pac_id")