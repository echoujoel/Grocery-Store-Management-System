"""Verify transaction accuracy, rejected purchases, and atomic persistence."""

from copy import deepcopy
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from customers import register_customer
from main import main
from products import add_product, update_product
from sales import calculate_total, display_sales, record_sale
from storage import StorageError, create_empty_store, load_store, save_store, validate_store


def create_test_store():
    """Build a small valid store without reading actual store records."""
    store = create_empty_store()
    add_product(store["products"], "P001", "Rice", "5000", "20")
    register_customer(store["customers"], "C001", "Joel", "joel@example.com")
    return store


class SalesTests(unittest.TestCase):
    def setUp(self):
        self.store = create_test_store()

    def test_successful_sale_records_every_field_and_reduces_stock(self):
        sale = record_sale(self.store, " C001 ", " P001 ", "3")
        self.assertEqual(sale, {
            "sale_id": "S001", "customer_id": "C001", "product_id": "P001",
            "quantity": 3, "total_price": "15000.00",
        })
        self.assertEqual(self.store["sales"], [sale])
        self.assertEqual(self.store["products"]["P001"]["quantity"], 17)

    def test_sale_keeps_customer_records_and_other_products_unchanged(self):
        add_product(self.store["products"], "P002", "Beans", "3000", "10")
        before = deepcopy(self.store)
        record_sale(self.store, "C001", "P001", "3")
        self.assertEqual(self.store["customers"], before["customers"])
        self.assertEqual(self.store["products"]["P002"], before["products"]["P002"])
        self.assertEqual(self.store["products"]["P001"]["price"], "5000.00")

    def test_buying_all_stock_succeeds_and_next_purchase_is_rejected(self):
        record_sale(self.store, "C001", "P001", "20")
        self.assertEqual(self.store["products"]["P001"]["quantity"], 0)
        before = deepcopy(self.store)
        with self.assertRaisesRegex(ValueError, "Insufficient stock"):
            record_sale(self.store, "C001", "P001", "1")
        self.assertEqual(self.store, before)

    def test_insufficient_stock_leaves_all_records_unchanged(self):
        before = deepcopy(self.store)
        with self.assertRaisesRegex(ValueError, "only 20 units"):
            record_sale(self.store, "C001", "P001", "21")
        self.assertEqual(self.store, before)

    def test_missing_or_blank_references_leave_all_records_unchanged(self):
        before = deepcopy(self.store)
        for customer_id, product_id in (("C999", "P001"), ("C001", "P999"),
                                        (" ", "P001"), ("C001", "")):
            with self.subTest(customer_id=customer_id, product_id=product_id):
                with self.assertRaises(ValueError):
                    record_sale(self.store, customer_id, product_id, "1")
                self.assertEqual(self.store, before)

    def test_invalid_purchase_quantities_do_not_create_sales(self):
        before = deepcopy(self.store)
        for quantity in ("0", 0, "-1", "1.5", "1.0", "1e1", "two", "", " ", True, 1.0, None):
            with self.subTest(quantity=quantity):
                with self.assertRaisesRegex(ValueError, "positive whole number"):
                    record_sale(self.store, "C001", "P001", quantity)
                self.assertEqual(self.store, before)

    def test_rejected_purchase_does_not_consume_a_sale_id(self):
        with self.assertRaises(ValueError):
            record_sale(self.store, "C001", "P001", "21")
        self.assertEqual(record_sale(self.store, "C001", "P001", "1")["sale_id"], "S001")

    def test_multiple_sales_receive_unique_ids_and_accumulate_stock_reductions(self):
        first = record_sale(self.store, "C001", "P001", "2")
        second = record_sale(self.store, "C001", "P001", "3")
        self.assertEqual([first["sale_id"], second["sale_id"]], ["S001", "S002"])
        self.assertEqual(self.store["products"]["P001"]["quantity"], 15)

    def test_generated_id_does_not_collide_with_imported_history(self):
        record_sale(self.store, "C001", "P001", "1")
        record_sale(self.store, "C001", "P001", "1")["sale_id"] = "S003"
        record_sale(self.store, "C001", "P001", "1")
        self.assertEqual(len({sale["sale_id"] for sale in self.store["sales"]}), 3)
        self.assertEqual(self.store["sales"][1]["sale_id"], "S003")

    def test_decimal_totals_are_exact(self):
        self.assertEqual(calculate_total("0.10", 3), "0.30")
        self.assertEqual(calculate_total("0.29", 3), "0.87")
        self.assertEqual(calculate_total("12.50", 3), "37.50")

    def test_large_totals_are_not_rounded_by_decimal_default_precision(self):
        self.assertEqual(calculate_total("9" * 30 + ".99", 3), "2" + "9" * 30 + ".97")

    def test_later_price_change_preserves_existing_sale_totals(self):
        record_sale(self.store, "C001", "P001", "3")
        update_product(self.store["products"], "P001", price="6000")
        record_sale(self.store, "C001", "P001", "2")
        self.assertEqual([sale["total_price"] for sale in self.store["sales"]],
                         ["15000.00", "12000.00"])
        validate_store(self.store)

    def test_historical_sale_quantity_is_not_compared_to_remaining_stock(self):
        record_sale(self.store, "C001", "P001", "20")
        validate_store(self.store)

    def test_sales_output_shows_all_required_fields_and_empty_message(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            display_sales([])
            record_sale(self.store, "C001", "P001", "3")
            display_sales(self.store["sales"])
        for value in ("No sales recorded", "Sale ID", "Customer ID", "Product ID",
                      "Quantity", "Total", "S001", "C001", "P001", "15000.00"):
            self.assertIn(value, output.getvalue())

    def test_invalid_transaction_fields_are_rejected_at_storage_boundary(self):
        sale = record_sale(self.store, "C001", "P001", "1")
        invalid_records = [
            {}, {**sale, "sale_id": ""}, {**sale, "sale_id": " S001 "},
            {**sale, "customer_id": "C999"}, {**sale, "product_id": "P999"},
            {**sale, "customer_id": " C001 "}, {**sale, "product_id": None},
            {**sale, "quantity": 0}, {**sale, "quantity": -1},
            {**sale, "quantity": True}, {**sale, "quantity": "1"},
            {**sale, "quantity": 1.5}, {**sale, "total_price": "0"},
            {**sale, "total_price": "-5"}, {**sale, "total_price": "1.234"},
            {**sale, "total_price": "NaN"}, {**sale, "extra": "unexpected"},
        ]
        for invalid in invalid_records:
            with self.subTest(sale=invalid):
                store = deepcopy(self.store)
                store["sales"] = [invalid]
                with self.assertRaisesRegex(StorageError, "Invalid sales data"):
                    validate_store(store)

    def test_duplicate_sale_ids_are_rejected(self):
        sale = record_sale(self.store, "C001", "P001", "1")
        self.store["sales"].append(dict(sale))
        with self.assertRaisesRegex(StorageError, "Duplicate sale ID"):
            validate_store(self.store)

    def test_saved_sales_stock_and_unique_ids_survive_reloading(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "store.json"
            record_sale(self.store, "C001", "P001", "3")
            save_store(self.store, path)
            restarted_store = load_store(path)
            self.assertEqual(restarted_store, self.store)
            sale = record_sale(restarted_store, "C001", "P001", "2")
            self.assertEqual(sale["sale_id"], "S002")
            save_store(restarted_store, path)
            self.assertEqual(load_store(path)["products"]["P001"]["quantity"], 15)
            self.assertEqual(len(load_store(path)["sales"]), 2)

    def test_failed_file_replacement_preserves_stock_and_sales_on_disk(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "store.json"
            save_store(self.store, path)
            original_bytes = path.read_bytes()
            draft = deepcopy(self.store)
            record_sale(draft, "C001", "P001", "3")
            with patch("storage.os.replace", side_effect=PermissionError("File is locked")):
                with self.assertRaises(StorageError):
                    save_store(draft, path)
            self.assertEqual(path.read_bytes(), original_bytes)
            self.assertEqual(load_store(path), self.store)
            self.assertEqual(list(path.parent.glob(".store-*.tmp")), [])


class SalesMenuTests(unittest.TestCase):
    def run_menu(self, inputs, store=None, save_error=None):
        store = create_test_store() if store is None else store
        output = io.StringIO()
        with patch("main.load_store", return_value=store):
            with patch("main.save_store", side_effect=save_error):
                with patch("builtins.input", side_effect=inputs):
                    with contextlib.redirect_stdout(output):
                        status = main()
        return status, output.getvalue()

    def test_sale_is_confirmed_and_visible_in_history_and_inventory(self):
        status, output = self.run_menu(["6", "C001", "P001", "3", "3", "7", "8"])
        self.assertEqual(status, 0)
        self.assertIn("Sale 'S001' recorded and saved. Total: 15000.00", output)
        self.assertIn("Sales transactions", output)
        self.assertIn("17", output)
        self.assertIn("C001", output)

    def test_sale_without_products_explains_what_to_add(self):
        store = create_test_store()
        store["products"] = {}
        status, output = self.run_menu(["6", "8"], store=store)
        self.assertEqual(status, 0)
        self.assertIn("Add a product with option 1", output)

    def test_missing_customer_or_product_returns_to_menu_without_extra_prompts(self):
        for inputs in (["6", "C999", "7", "8"], ["6", "C001", "P999", "7", "8"]):
            with self.subTest(inputs=inputs):
                status, output = self.run_menu(inputs)
                self.assertEqual(status, 0)
                self.assertIn("does not exist", output)
                self.assertIn("No sales recorded", output)

    def test_invalid_or_excessive_quantity_returns_to_menu_without_sale(self):
        for quantity in ("0", "-1", "1.5", "invalid", "21"):
            with self.subTest(quantity=quantity):
                store = create_test_store()
                before = deepcopy(store)
                status, output = self.run_menu(
                    ["6", "C001", "P001", quantity, "7", "8"], store=store,
                    save_error=AssertionError("A rejected sale should not be saved"),
                )
                self.assertEqual(status, 0)
                self.assertIn("Invalid input:", output)
                self.assertIn("No sales recorded", output)
                self.assertEqual(store, before)

    def test_failed_sale_save_does_not_reduce_live_stock_or_report_success(self):
        store = create_test_store()
        before = deepcopy(store)
        status, output = self.run_menu(
            ["6", "C001", "P001", "3", "3", "7", "8"], store=store,
            save_error=StorageError("Disk is full"),
        )
        self.assertEqual(status, 0)
        self.assertIn("Change was not saved", output)
        self.assertIn("No sales recorded", output)
        self.assertNotIn("recorded and saved", output)
        self.assertEqual(store, before)

    def test_interrupted_sale_entry_does_not_attempt_save(self):
        for interruption in (EOFError(), KeyboardInterrupt()):
            with self.subTest(interruption=type(interruption).__name__):
                status, output = self.run_menu(
                    ["6", "C001", "P001", interruption],
                    save_error=AssertionError("Incomplete sales should not be saved"),
                )
                self.assertEqual(status, 0)
                self.assertIn("Goodbye!", output)

    def test_sales_price_changes_and_stock_survive_menu_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "store.json"
            save_store(create_test_store(), path)
            output = io.StringIO()
            inputs = ["6", "C001", "P001", "3",
                      "2", "P001", "", "6000", "",
                      "6", "C001", "P001", "2", "7", "8"]
            with patch("main.load_store", side_effect=lambda: load_store(path)):
                with patch("main.save_store", side_effect=lambda store: save_store(store, path)):
                    with patch("builtins.input", side_effect=inputs):
                        with contextlib.redirect_stdout(output):
                            self.assertEqual(main(), 0)
            saved = load_store(path)
            self.assertEqual(saved["products"]["P001"]["quantity"], 15)
            self.assertEqual([sale["total_price"] for sale in saved["sales"]],
                             ["15000.00", "12000.00"])

            restarted_output = io.StringIO()
            with patch("main.load_store", side_effect=lambda: load_store(path)):
                with patch("main.save_store", side_effect=lambda store: save_store(store, path)):
                    with patch("builtins.input", side_effect=["6", "C001", "P001", "1", "8"]):
                        with contextlib.redirect_stdout(restarted_output):
                            self.assertEqual(main(), 0)
            self.assertIn("Sale 'S003' recorded and saved. Total: 6000.00", restarted_output.getvalue())
            self.assertEqual(load_store(path)["products"]["P001"]["quantity"], 14)


if __name__ == "__main__":
    unittest.main()
