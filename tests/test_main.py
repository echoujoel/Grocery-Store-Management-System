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

    def test_sales_options_explain_missing_customer_and_empty_history(self):
        status, output = self.run_menu(["6", "7", "8"])
        self.assertEqual(status, 0)
        self.assertIn("Register a customer with option 4", output)
        self.assertIn("No sales recorded", output)
        self.assertEqual(output.count("1. Add a product"), 3)

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
        self.assertIn("Invalid input:", output)
        self.assertIn("No products in inventory", output)

    def test_failed_add_save_leaves_live_inventory_unchanged(self):
        store = create_empty_store()
        status, output = self.run_menu(
            ["1", "P001", "Rice", "5000", "20", "3", "8"],
            store=store, save_error=StorageError("Disk is full"),
        )
        self.assertEqual(status, 0)
        self.assertIn("Change was not saved", output)
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
        self.assertIn("Change was not saved", output)
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

    def test_register_and_display_customer_from_menu(self):
        status, output = self.run_menu(
            ["4", " C001 ", " Joel ", " joel@EXAMPLE.COM ", "5", "8"]
        )
        self.assertEqual(status, 0)
        self.assertIn("Customer 'C001' registered and saved.", output)
        self.assertIn("Joel", output)
        self.assertIn("joel@example.com", output)

    def test_duplicate_customer_id_returns_to_menu_without_extra_prompts(self):
        status, output = self.run_menu(
            ["4", "C001", "Joel", "joel@example.com", "4", " C001 ", "5", "8"]
        )
        self.assertEqual(status, 0)
        self.assertIn("Customer ID 'C001' already exists.", output)
        self.assertEqual(output.count("registered and saved"), 1)

    def test_invalid_customer_input_returns_to_menu_without_registering(self):
        invalid_inputs = [
            ["4", " ", "5", "8"],
            ["4", "C001", " ", "joel@example.com", "5", "8"],
            ["4", "C001", "Joel", "invalid-email", "5", "8"],
        ]
        for inputs in invalid_inputs:
            with self.subTest(inputs=inputs):
                status, output = self.run_menu(inputs)
                self.assertEqual(status, 0)
                self.assertIn("Invalid input:", output)
                self.assertIn("No registered customers", output)
                self.assertNotIn("registered and saved", output)

    def test_failed_customer_save_keeps_live_records_unchanged(self):
        store = create_empty_store()
        status, output = self.run_menu(
            ["4", "C001", "Joel", "joel@example.com", "5", "8"],
            store=store, save_error=StorageError("Disk is full"),
        )
        self.assertEqual(status, 0)
        self.assertIn("Change was not saved", output)
        self.assertIn("No registered customers", output)
        self.assertNotIn("registered and saved", output)
        self.assertEqual(store["customers"], {})

    def test_interrupted_customer_entry_does_not_attempt_save(self):
        for interruption in (EOFError(), KeyboardInterrupt()):
            with self.subTest(interruption=type(interruption).__name__):
                status, output = self.run_menu(
                    ["4", "C001", "Joel", interruption],
                    save_error=AssertionError("Incomplete registration should not be saved"),
                )
                self.assertEqual(status, 0)
                self.assertIn("Goodbye!", output)
                self.assertNotIn("registered and saved", output)

    def test_customer_workflow_persists_and_preserves_other_records(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "store.json"
            original = create_empty_store()
            original["products"]["P001"] = {"name": "Rice", "price": "5000.00", "quantity": 17}
            original["customers"]["C001"] = {"name": "Joel", "email": "joel@example.com"}
            original["sales"] = [{"sale_id": "S001", "customer_id": "C001", "product_id": "P001",
                                  "quantity": 3, "total_price": 15000}]
            save_store(original, path)
            output = io.StringIO()
            with patch("main.load_store", side_effect=lambda: load_store(path)):
                with patch("main.save_store", side_effect=lambda store: save_store(store, path)):
                    with patch("builtins.input", side_effect=[
                        "4", "C002", "Jane", "jane@example.com", "8",
                    ]):
                        with contextlib.redirect_stdout(output):
                            self.assertEqual(main(), 0)
            saved = load_store(path)
            self.assertEqual(saved["customers"]["C002"], {
                "name": "Jane", "email": "jane@example.com",
            })
            self.assertEqual(saved["products"], original["products"])
            self.assertEqual(saved["customers"]["C001"], original["customers"]["C001"])
            self.assertEqual(saved["sales"], original["sales"])

            restarted_output = io.StringIO()
            with patch("main.load_store", side_effect=lambda: load_store(path)):
                with patch("builtins.input", side_effect=["5", "8"]):
                    with contextlib.redirect_stdout(restarted_output):
                        self.assertEqual(main(), 0)
            self.assertIn("1 products, 2 customers, 1 sales", restarted_output.getvalue())
            self.assertIn("jane@example.com", restarted_output.getvalue())

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
