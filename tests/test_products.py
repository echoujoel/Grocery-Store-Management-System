"""Check inventory rules and preservation of records on rejected changes."""

from copy import deepcopy
import contextlib
import io
import unittest

from products import add_product, display_products, get_product, update_product
from storage import StorageError, create_empty_store, validate_store


class ProductTests(unittest.TestCase):
    def setUp(self):
        self.products = {}
        add_product(self.products, "P001", "Rice", "5000", "20")

    def test_add_trims_fields_and_stores_exact_price_and_integer_stock(self):
        add_product(self.products, " P002 ", " Beans ", " 12.50 ", " 0 ")
        self.assertEqual(self.products["P002"], {
            "name": "Beans", "price": "12.50", "quantity": 0,
        })

    def test_price_accepts_one_decimal_place_and_small_positive_amounts(self):
        add_product(self.products, "P002", "Beans", "12.5", "3")
        add_product(self.products, "P003", "Salt", "0.01", "1")
        self.assertEqual(self.products["P002"]["price"], "12.50")
        self.assertEqual(self.products["P003"]["price"], "0.01")

    def test_duplicate_id_does_not_overwrite_product(self):
        before = deepcopy(self.products)
        with self.assertRaisesRegex(ValueError, "already exists"):
            add_product(self.products, " P001 ", "Different rice", "100", "1")
        self.assertEqual(self.products, before)

    def test_invalid_additions_leave_inventory_unchanged(self):
        invalid_fields = [
            ("", "Rice", "1", "1"),
            ("  ", "Rice", "1", "1"),
            ("P002", "  ", "1", "1"),
            ("P002", "Rice", "0", "1"),
            ("P002", "Rice", "-5", "1"),
            ("P002", "Rice", "1.234", "1"),
            ("P002", "Rice", "NaN", "1"),
            ("P002", "Rice", "Infinity", "1"),
            ("P002", "Rice", "1e3", "1"),
            ("P002", "Rice", "5,000", "1"),
            ("P002", "Rice", "", "1"),
            ("P002", "Rice", True, "1"),
            ("P002", "Rice", "1", "-1"),
            ("P002", "Rice", "1", "1.5"),
            ("P002", "Rice", "1", "two"),
            ("P002", "Rice", "1", ""),
            ("P002", "Rice", "1", 1.0),
            ("P002", "Rice", "1", True),
        ]
        before = deepcopy(self.products)
        for fields in invalid_fields:
            with self.subTest(fields=fields):
                with self.assertRaises(ValueError):
                    add_product(self.products, *fields)
                self.assertEqual(self.products, before)

    def test_update_all_fields_preserves_product_id(self):
        changed = update_product(self.products, " P001 ", " Brown rice ", "6500.50", "7")
        self.assertTrue(changed)
        self.assertEqual(self.products, {
            "P001": {"name": "Brown rice", "price": "6500.50", "quantity": 7},
        })

    def test_partial_update_keeps_other_fields_and_accepts_zero_stock(self):
        update_product(self.products, "P001", quantity="0")
        self.assertEqual(self.products["P001"], {
            "name": "Rice", "price": "5000.00", "quantity": 0,
        })

    def test_empty_update_reports_no_change(self):
        before = deepcopy(self.products)
        self.assertFalse(update_product(self.products, "P001"))
        self.assertEqual(self.products, before)

    def test_invalid_update_does_not_apply_other_valid_fields(self):
        before = deepcopy(self.products)
        for fields in ({"name": "Beans", "price": "-5"},
                       {"name": "Beans", "price": "12", "quantity": "-1"},
                       {"name": ""}):
            with self.subTest(fields=fields):
                with self.assertRaises(ValueError):
                    update_product(self.products, "P001", **fields)
                self.assertEqual(self.products, before)

    def test_missing_product_cannot_be_updated(self):
        with self.assertRaisesRegex(ValueError, "does not exist"):
            update_product(self.products, "P999", price="50")
        self.assertNotIn("P999", self.products)

    def test_lookup_trims_id_and_reports_blank_or_missing_ids(self):
        self.assertEqual(get_product(self.products, " P001 ")["name"], "Rice")
        for product_id in (" ", "P999"):
            with self.subTest(product_id=product_id):
                with self.assertRaises(ValueError):
                    get_product(self.products, product_id)

    def test_inventory_output_contains_all_fields_and_empty_message(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            display_products({})
            display_products(self.products)
        for value in ("No products in inventory", "P001", "Rice", "5000.00", "20"):
            self.assertIn(value, output.getvalue())

    def test_invalid_product_records_are_rejected_at_storage_boundary(self):
        invalid_records = [
            {"name": "Rice"},
            {"name": " ", "price": "5.00", "quantity": 1},
            {"name": "Rice", "price": 0, "quantity": 1},
            {"name": "Rice", "price": "5.123", "quantity": 1},
            {"name": "Rice", "price": "5.00", "quantity": -1},
            {"name": "Rice", "price": "5.00", "quantity": "1"},
            {"name": "Rice", "price": "5.00", "quantity": True},
        ]
        for record in invalid_records:
            with self.subTest(record=record):
                store = create_empty_store()
                store["products"]["P001"] = record
                with self.assertRaises(StorageError):
                    validate_store(store)

    def test_stored_ids_with_surrounding_spaces_are_rejected(self):
        store = create_empty_store()
        store["products"][" P001 "] = self.products["P001"]
        with self.assertRaises(StorageError):
            validate_store(store)


if __name__ == "__main__":
    unittest.main()
