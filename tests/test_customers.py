"""Verify customer registration, validation, and customer list output."""

from copy import deepcopy
import contextlib
import io
import unittest

from customers import display_customers, normalize_email, register_customer
from storage import StorageError, create_empty_store, validate_store


class CustomerTests(unittest.TestCase):
    def setUp(self):
        self.customers = {}
        register_customer(self.customers, "C001", "Joel", "joel@example.com")

    def test_registration_trims_fields_and_keeps_unicode_names(self):
        register_customer(self.customers, " C002 ", " José ", " Jose@EXAMPLE.COM ")
        self.assertEqual(self.customers["C002"], {
            "name": "José", "email": "Jose@example.com",
        })

    def test_duplicate_trimmed_id_preserves_original_customer(self):
        before = deepcopy(self.customers)
        with self.assertRaisesRegex(ValueError, "already exists"):
            register_customer(self.customers, " C001 ", "Another person", "other@example.com")
        self.assertEqual(self.customers, before)

    def test_customer_ids_are_case_sensitive(self):
        register_customer(self.customers, "c001", "Jane", "jane@example.com")
        self.assertEqual(set(self.customers), {"C001", "c001"})

    def test_email_does_not_have_to_be_unique(self):
        register_customer(self.customers, "C002", "Jane", "joel@example.com")
        self.assertEqual(len(self.customers), 2)

    def test_blank_or_nontext_fields_do_not_register_a_customer(self):
        before = deepcopy(self.customers)
        invalid_fields = [
            ("", "Jane", "jane@example.com"),
            ("  ", "Jane", "jane@example.com"),
            (12, "Jane", "jane@example.com"),
            ("C002", "  ", "jane@example.com"),
            ("C002", None, "jane@example.com"),
            ("C002", "Jane", "  "),
            ("C002", "Jane", None),
        ]
        for fields in invalid_fields:
            with self.subTest(fields=fields):
                with self.assertRaises(ValueError):
                    register_customer(self.customers, *fields)
                self.assertEqual(self.customers, before)

    def test_common_email_formats_are_accepted(self):
        for email in ("joel@example.com", "joel.smith+shop@example.co.ug",
                      "joel_1@example-store.com", "joel%shop@sub.example.com"):
            with self.subTest(email=email):
                self.assertEqual(normalize_email(email), email)

    def test_malformed_email_rejects_registration_without_changes(self):
        before = deepcopy(self.customers)
        invalid_emails = [
            "joel", "joel@", "@example.com", "joel@@example.com", "joel@example",
            "jo el@example.com", "joel@exam ple.com", "joel\n@example.com",
            ".joel@example.com", "joel.@example.com", "joel..smith@example.com",
            "joel@example..com", "joel@.example.com", "joel@example.com.",
            "joel@-example.com", "joel@example-.com", "joel@exam_ple.com",
            "a" * 65 + "@example.com", "joel@" + "a" * 64 + ".com",
            "a" * 64 + "@" + ".".join(["b" * 63] * 3),
        ]
        for email in invalid_emails:
            with self.subTest(email=email):
                with self.assertRaises(ValueError):
                    register_customer(self.customers, "C002", "Jane", email)
                self.assertEqual(self.customers, before)

    def test_customer_list_contains_all_customers_and_fields(self):
        register_customer(self.customers, "C002", "Jane", "jane@example.com")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            display_customers(self.customers)
        for value in ("C001", "Joel", "joel@example.com", "C002", "Jane", "jane@example.com"):
            self.assertIn(value, output.getvalue())

    def test_empty_customer_list_explains_how_to_register(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            display_customers({})
        self.assertIn("No registered customers", output.getvalue())
        self.assertIn("option 4", output.getvalue())

    def test_invalid_customer_fields_are_rejected_at_storage_boundary(self):
        invalid_records = [
            {}, {"name": "Jane"}, {"email": "jane@example.com"},
            {"name": " ", "email": "jane@example.com"},
            {"name": 12, "email": "jane@example.com"},
            {"name": "Jane", "email": "invalid"},
            {"name": "Jane", "email": None},
            {"name": "Jane", "email": "jane@example.com", "extra": "unexpected"},
        ]
        for customer in invalid_records:
            with self.subTest(customer=customer):
                store = create_empty_store()
                store["customers"]["C001"] = customer
                with self.assertRaisesRegex(StorageError, "Invalid customer data"):
                    validate_store(store)

    def test_stored_ids_with_surrounding_spaces_are_rejected(self):
        store = create_empty_store()
        store["customers"][" C001 "] = self.customers["C001"]
        with self.assertRaises(StorageError):
            validate_store(store)


if __name__ == "__main__":
    unittest.main()
