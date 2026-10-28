"""Verify menu navigation and safe startup without touching real store data."""

import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from main import main
from storage import StorageError, create_empty_store, load_store, save_store


class MenuTests(unittest.TestCase):
    def run_menu(self, inputs, store=None, save_error=None):
        output = io.StringIO()
        store = create_empty_store() if store is None else store
        with patch("main.load_store", return_value=store):
            with patch("main.save_store", side_effect=save_error):
                with patch("builtins.input", side_effect=inputs):
                    with contextlib.redirect_stdout(output):
                        status = main()
        return status, output.getvalue()

    def test_exit_option_closes_application(self):
        status, output = self.run_menu([" 8 "])
        self.assertEqual(status, 0)
        self.assertIn("Goodbye!", output)

    def test_invalid_inputs_repeat_menu(self):
        status, output = self.run_menu(["", "hello", "0", "9", "2.5", "8"])
        self.assertEqual(status, 0)
        self.assertEqual(output.count("Invalid choice."), 5)
        self.assertEqual(output.count("1. Add a product"), 6)

    def test_upcoming_options_explain_status_and_keep_menu_running(self):
        status, output = self.run_menu(["4", "5", "6", "7", "8"])
        self.assertEqual(status, 0)
        self.assertEqual(output.count("will be available"), 4)
        self.assertEqual(output.count("1. Add a product"), 5)

    def test_add_and_display_product_from_menu(self):
        status, output = self.run_menu(["1", "P001", "Rice", "5000", "20", "3", "8"])
        self.assertEqual(status, 0)
        self.assertIn("Product 'P001' added and saved.", output)
        self.assertIn("Rice", output)
        self.assertIn("5000.00", output)

    def test_duplicate_and_missing_ids_return_to_menu_without_more_prompts(self):
        inputs = ["1", "P001", "Rice", "5000", "20",
                  "1", " P001 ", "2", "P999", "3", "8"]
        status, output = self.run_menu(inputs)
        self.assertEqual(status, 0)
        self.assertIn("already exists", output)
        self.assertIn("does not exist", output)

    def test_invalid_product_values_return_to_menu_without_adding_product(self):
        status, output = self.run_menu(["1", "P001", "Rice", "-5", "20", "3", "8"])
        self.assertEqual(status, 0)
        self.assertIn("Invalid product:", output)
        self.assertIn("No products in inventory", output)

    def test_failed_add_save_leaves_live_inventory_unchanged(self):
        store = create_empty_store()
        status, output = self.run_menu(
            ["1", "P001", "Rice", "5000", "20", "3", "8"],
            store=store, save_error=StorageError("Disk is full"),
        )
        self.assertEqual(status, 0)
        self.assertIn("Product change was not saved", output)
        self.assertIn("No products in inventory", output)
        self.assertNotIn("added and saved", output)
        self.assertEqual(store["products"], {})

    def test_failed_update_save_keeps_old_product(self):
        store = create_empty_store()
        store["products"]["P001"] = {"name": "Rice", "price": "5000.00", "quantity": 20}
        status, output = self.run_menu(
            ["2", "P001", "Beans", "2500", "10", "3", "8"],
            store=store, save_error=StorageError("File is locked"),
        )
        self.assertEqual(status, 0)
        self.assertIn("Product change was not saved", output)
        self.assertIn("Rice", output)
        self.assertNotIn("updated and saved", output)
        self.assertEqual(store["products"]["P001"]["name"], "Rice")

    def test_blank_update_fields_do_not_attempt_save(self):
        store = create_empty_store()
        store["products"]["P001"] = {"name": "Rice", "price": "5000.00", "quantity": 20}
        status, output = self.run_menu(
            ["2", "P001", "", "", "", "8"], store=store,
            save_error=AssertionError("An unchanged record should not be saved"),
        )
        self.assertEqual(status, 0)
        self.assertIn("No changes made.", output)

    def test_interrupted_product_entry_discards_incomplete_input(self):
        for interruption in (EOFError(), KeyboardInterrupt()):
            with self.subTest(interruption=type(interruption).__name__):
                status, output = self.run_menu(
                    ["1", "P001", "Rice", interruption],
                    save_error=AssertionError("Incomplete input should not be saved"),
                )
                self.assertEqual(status, 0)
                self.assertIn("Goodbye!", output)

    def test_product_workflow_is_persisted_and_loaded_on_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "store.json"
            inputs = ["1", "P001", "Rice", "5000", "20",
                      "2", "P001", "Brown rice", "6500.50", "0", "8"]
            output = io.StringIO()
            with patch("main.load_store", side_effect=lambda: load_store(path)):
                with patch("main.save_store", side_effect=lambda store: save_store(store, path)):
                    with patch("builtins.input", side_effect=inputs):
                        with contextlib.redirect_stdout(output):
                            self.assertEqual(main(), 0)
            self.assertEqual(load_store(path)["products"], {
                "P001": {"name": "Brown rice", "price": "6500.50", "quantity": 0},
            })
            with patch("main.load_store", side_effect=lambda: load_store(path)):
                with patch("builtins.input", side_effect=["3", "8"]):
                    with contextlib.redirect_stdout(output):
                        self.assertEqual(main(), 0)
            self.assertIn("Store loaded: 1 products", output.getvalue())
            self.assertIn("Brown rice", output.getvalue())

    def test_end_of_input_and_keyboard_interrupt_exit_cleanly(self):
        for interruption in (EOFError(), KeyboardInterrupt()):
            with self.subTest(interruption=type(interruption).__name__):
                status, output = self.run_menu([interruption])
                self.assertEqual(status, 0)
                self.assertIn("Goodbye!", output)

    def test_storage_error_stops_before_prompting(self):
        output = io.StringIO()
        with patch("main.load_store", side_effect=StorageError("Invalid file")):
            with patch("builtins.input") as prompt:
                with contextlib.redirect_stdout(output):
                    status = main()
        self.assertEqual(status, 1)
        prompt.assert_not_called()
        self.assertIn("Unable to start: Invalid file", output.getvalue())


if __name__ == "__main__":
    unittest.main()
