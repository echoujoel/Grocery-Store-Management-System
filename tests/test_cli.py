"""Acceptance checks that run the real terminal program in isolated copies."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_FILES = ("main.py", "products.py", "customers.py", "sales.py", "storage.py", "validation.py")


class TerminalAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.working_directory = Path(self.directory.name)
        self.application = self.working_directory / "application"
        self.application.mkdir()
        for filename in SOURCE_FILES:
            shutil.copy2(PROJECT_ROOT / filename, self.application / filename)
        self.data_path = self.application / "data" / "store.json"

    def run_application(self, inputs):
        """Use the public entry point from a different working directory."""
        return subprocess.run(
            [sys.executable, str(self.application / "main.py")],
            input="\n".join(inputs) + "\n",
            capture_output=True,
            text=True,
            encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            cwd=self.working_directory,
            timeout=15,
            check=False,
        )

    def read_store(self):
        return json.loads(self.data_path.read_text(encoding="utf-8"))

    def seed_store_through_menu(self):
        result = self.run_application([
            "1", "P001", "Rice", "5000", "20",
            "4", "C001", "Joel", "joel@example.com", "8",
        ])
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_all_eight_options_and_records_survive_real_process_restart(self):
        result = self.run_application([
            "1", "P001", "Rice", "5000", "20",
            "2", "P001", "Brown rice", "5500", "15", "3",
            "4", "C001", "Joel", "joel@example.com", "5",
            "6", "C001", "P001", "3", "7", "8",
        ])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        for text in ("added and saved", "updated and saved", "Product inventory",
                     "registered and saved", "Registered customers", "Sales transactions",
                     "Sale 'S001' recorded and saved. Total: 16500.00", "Goodbye!"):
            self.assertIn(text, result.stdout)
        self.assertEqual(self.read_store(), {
            "products": {"P001": {"name": "Brown rice", "price": "5500.00", "quantity": 12}},
            "customers": {"C001": {"name": "Joel", "email": "joel@example.com"}},
            "sales": [{"sale_id": "S001", "customer_id": "C001", "product_id": "P001",
                       "quantity": 3, "total_price": "16500.00"}],
        })
        self.assertFalse((self.working_directory / "data").exists())

        restarted = self.run_application([
            "3", "5", "7", "2", "P001", "", "6000", "",
            "6", "C001", "P001", "2", "8",
        ])
        self.assertEqual(restarted.returncode, 0, restarted.stderr)
        self.assertEqual(restarted.stderr, "")
        self.assertIn("Store loaded: 1 products, 1 customers, 1 sales.", restarted.stdout)
        self.assertIn("Sale 'S002' recorded and saved. Total: 12000.00", restarted.stdout)
        saved = self.read_store()
        self.assertEqual(saved["products"]["P001"]["quantity"], 10)
        self.assertEqual(saved["sales"][0]["total_price"], "16500.00")
        self.assertEqual(len(saved["sales"]), 2)

    def test_rejected_operations_leave_json_file_byte_for_byte_unchanged(self):
        self.seed_store_through_menu()
        original = self.data_path.read_bytes()
        result = self.run_application([
            "invalid-menu-choice", "1", "P001",
            "1", "P002", "Beans", "-5", "10",
            "4", "C002", "Jane", "invalid-email", "4", "C001",
            "2", "P999", "2", "P001", "Changed name", "-5", "",
            "6", "C999", "6", "C001", "P999",
            "6", "C001", "P001", "0", "6", "C001", "P001", "-1",
            "6", "C001", "P001", "1.5", "6", "C001", "P001", "21",
            "3", "5", "7", "8",
        ])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        for text in ("Invalid choice", "already exists", "does not exist",
                     "positive whole number", "Insufficient stock", "No sales recorded"):
            self.assertIn(text, result.stdout)
        self.assertEqual(self.data_path.read_bytes(), original)

    def test_last_units_can_be_sold_and_empty_stock_cannot_be_sold_again(self):
        self.seed_store_through_menu()
        result = self.run_application([
            "6", "C001", "P001", "20", "6", "C001", "P001", "1", "7", "8",
        ])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Total: 100000.00", result.stdout)
        self.assertIn("Insufficient stock: only 0 units available", result.stdout)
        self.assertEqual(self.read_store()["products"]["P001"]["quantity"], 0)
        self.assertEqual(len(self.read_store()["sales"]), 1)

    def test_bad_json_stops_startup_without_traceback_or_overwriting_file(self):
        self.data_path.parent.mkdir()
        for contents in ("{broken", "[]", '{"products": {}, "products": {}, "customers": {}, "sales": []}'):
            with self.subTest(contents=contents):
                self.data_path.write_text(contents, encoding="utf-8")
                result = self.run_application(["8"])
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stderr, "")
                self.assertIn("Unable to start:", result.stdout)
                self.assertEqual(self.data_path.read_text(encoding="utf-8"), contents)

    def test_eof_during_entry_exits_without_creating_partial_record(self):
        result = self.run_application(["1", "P001"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Goodbye!", result.stdout)
        self.assertEqual(self.read_store(), {"products": {}, "customers": {}, "sales": []})


if __name__ == "__main__":
    unittest.main()
