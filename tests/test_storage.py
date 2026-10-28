"""Verify persistence and protection of existing store records."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from storage import StorageError, create_empty_store, load_store, save_store


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "data" / "store.json"

    def test_first_run_creates_empty_json_file(self):
        store = load_store(self.path)
        self.assertEqual(store, {"products": {}, "customers": {}, "sales": []})
        self.assertEqual(json.loads(self.path.read_text(encoding="utf-8")), store)

    def test_empty_stores_do_not_share_mutable_collections(self):
        first = create_empty_store()
        first["products"]["P001"] = {"name": "Rice"}
        self.assertEqual(create_empty_store()["products"], {})

    def test_records_survive_save_and_reload(self):
        store = {
            "products": {"P001": {"name": "Café rice", "price": 5000, "quantity": 17}},
            "customers": {"C001": {"name": "Joel", "email": "joel@example.com"}},
            "sales": [{"sale_id": "S001", "customer_id": "C001", "product_id": "P001",
                       "quantity": 3, "total_price": 15000}],
        }
        save_store(store, self.path)
        self.assertEqual(load_store(self.path), store)

    def test_bad_existing_files_are_preserved(self):
        invalid_contents = [
            "{broken json", "", "null", "[]", "{}",
            '{"products": [], "customers": {}, "sales": []}',
            '{"products": {}, "customers": [], "sales": []}',
            '{"products": {}, "customers": {"C001": {}}, "sales": []}',
            '{"products": {}, "customers": {"C001": {"name": "Joel", "email": "invalid"}}, "sales": []}',
            '{"products": {}, "customers": {}, "sales": {}}',
            '{"products": {"": {}}, "customers": {}, "sales": []}',
            '{"products": {"P001": 1}, "customers": {}, "sales": []}',
            '{"products": {}, "customers": {}, "sales": [1]}',
            '{"products": {}, "customers": {}, "sales": [{}]}',
            '{"products": {"P001": {"price": NaN}}, "customers": {}, "sales": []}',
        ]
        self.path.parent.mkdir()
        for contents in invalid_contents:
            with self.subTest(contents=contents):
                self.path.write_text(contents, encoding="utf-8")
                with self.assertRaises(StorageError):
                    load_store(self.path)
                self.assertEqual(self.path.read_text(encoding="utf-8"), contents)

    def test_invalid_encoding_is_reported_and_preserved(self):
        self.path.parent.mkdir()
        self.path.write_bytes(b"\xff\xfe")
        with self.assertRaises(StorageError):
            load_store(self.path)
        self.assertEqual(self.path.read_bytes(), b"\xff\xfe")

    def test_duplicate_json_keys_are_reported_without_discarding_records(self):
        duplicate_key_files = [
            '{"products": {}, "products": {}, "customers": {}, "sales": []}',
            '{"products": {}, "customers": {"C001": {"name": "Joel", "email": "joel@example.com"}, '
            '"C001": {"name": "Jane", "email": "jane@example.com"}}, "sales": []}',
            '{"products": {}, "customers": {"C001": {"name": "Joel", "name": "Jane", '
            '"email": "joel@example.com"}}, "sales": []}',
        ]
        self.path.parent.mkdir()
        for contents in duplicate_key_files:
            with self.subTest(contents=contents):
                self.path.write_text(contents, encoding="utf-8")
                with self.assertRaisesRegex(StorageError, "Duplicate JSON key"):
                    load_store(self.path)
                self.assertEqual(self.path.read_text(encoding="utf-8"), contents)

    def test_excessively_nested_json_is_reported_and_preserved(self):
        self.path.parent.mkdir()
        contents = "[" * 2000 + "0" + "]" * 2000
        self.path.write_text(contents, encoding="utf-8")
        with self.assertRaises(StorageError):
            load_store(self.path)
        self.assertEqual(self.path.read_text(encoding="utf-8"), contents)

    def test_invalid_save_preserves_existing_records(self):
        original = load_store(self.path)
        original_bytes = self.path.read_bytes()
        invalid_stores = [
            {},
            {"products": {1: {}}, "customers": {}, "sales": []},
            {"products": {"P001": {"price": float("inf")}}, "customers": {}, "sales": []},
            {"products": {"P001": {"name": object()}}, "customers": {}, "sales": []},
            {"products": {}, "customers": {"C001": {"name": "Joel", "email": "invalid"}}, "sales": []},
        ]
        for store in invalid_stores:
            with self.subTest(store=store):
                with self.assertRaises(StorageError):
                    save_store(store, self.path)
                self.assertEqual(self.path.read_bytes(), original_bytes)
        self.assertEqual(load_store(self.path), original)

    def test_failed_replacement_preserves_original_and_cleans_temporary_file(self):
        original = load_store(self.path)
        with patch("storage.os.replace", side_effect=PermissionError("File is locked")):
            with self.assertRaises(StorageError):
                save_store(original, self.path)
        self.assertEqual(load_store(self.path), original)
        self.assertEqual(list(self.path.parent.glob(".store-*.tmp")), [])

    def test_unreadable_file_is_reported(self):
        with patch("storage.Path.open", side_effect=PermissionError("Access denied")):
            with self.assertRaises(StorageError):
                load_store(self.path)

    def test_directory_cannot_be_used_as_data_file(self):
        self.path.mkdir(parents=True)
        with self.assertRaises(StorageError):
            load_store(self.path)


if __name__ == "__main__":
    unittest.main()
