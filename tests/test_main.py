"""Verify menu navigation and safe startup without touching real store data."""

import contextlib
import io
import unittest
from unittest.mock import patch

from main import main
from storage import StorageError, create_empty_store


class MenuTests(unittest.TestCase):
    def run_menu(self, inputs):
        output = io.StringIO()
        with patch("main.load_store", return_value=create_empty_store()):
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
        status, output = self.run_menu(["1", "2", "3", "4", "5", "6", "7", "8"])
        self.assertEqual(status, 0)
        self.assertEqual(output.count("will be available"), 7)
        self.assertEqual(output.count("1. Add a product"), 8)

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
