"""Load and save grocery store records using Python's built-in JSON support."""

import json
import os
from pathlib import Path
import tempfile

from customers import validate_customers
from products import validate_products


# Resolve this relative to the source file, not the terminal's working directory.
DATA_FILE = Path(__file__).resolve().parent / "data" / "store.json"


class StorageError(Exception):
    """Report a storage problem that the terminal interface can explain."""


def create_empty_store():
    """Return new, independent collections for a store with no records."""
    return {"products": {}, "customers": {}, "sales": []}


def validate_store(data):
    """Check the collection structure before accepting or saving store data.

    Product and customer records are dictionaries keyed by their IDs. Sales
    are a list of record dictionaries. Product and customer fields are also
    checked; the sales milestone will add transaction field validation.
    """
    if not isinstance(data, dict) or set(data) != {"products", "customers", "sales"}:
        raise StorageError("Store data must contain products, customers, and sales.")

    for collection in ("products", "customers"):
        records = data[collection]
        if not isinstance(records, dict):
            raise StorageError(f"The {collection} collection must be a dictionary.")
        for record_id, record in records.items():
            if not isinstance(record_id, str) or not record_id.strip():
                raise StorageError(f"Each {collection} ID must be a nonempty string.")
            if not isinstance(record, dict):
                raise StorageError(f"Each {collection} record must be a dictionary.")

    try:
        validate_products(data["products"])
    except ValueError as error:
        raise StorageError(f"Invalid product data: {error}") from error

    try:
        validate_customers(data["customers"])
    except ValueError as error:
        raise StorageError(f"Invalid customer data: {error}") from error

    if not isinstance(data["sales"], list):
        raise StorageError("The sales collection must be a list.")
    if any(not isinstance(sale, dict) for sale in data["sales"]):
        raise StorageError("Each sales record must be a dictionary.")


def reject_nonfinite_number(value):
    """Reject NaN and Infinity, which are not valid JSON numbers."""
    raise ValueError(f"Invalid JSON number: {value}")


def load_store(file_path=DATA_FILE):
    """Read store records, creating an empty JSON file on the first run.

    Unreadable, malformed, or structurally invalid existing files raise
    StorageError and are left untouched.
    """
    path = Path(file_path)
    try:
        with path.open("r", encoding="utf-8") as source:
            data = json.load(source, parse_constant=reject_nonfinite_number)
    except FileNotFoundError:
        data = create_empty_store()
        save_store(data, path)
        return data
    except (OSError, ValueError) as error:
        raise StorageError(f"Could not read store data at {path}: {error}") from error

    validate_store(data)
    return data


def save_store(data, file_path=DATA_FILE):
    """Save all collections together without partially overwriting a file.

    Validate and serialize first, then write a temporary file in the same
    directory and replace the destination only after the write succeeds.
    This application is intended for one running instance at a time.
    """
    validate_store(data)
    try:
        contents = json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError, OverflowError) as error:
        raise StorageError(f"Store data could not be converted to JSON: {error}") from error

    path = Path(file_path)
    temporary_path = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=".store-",
            suffix=".tmp",
            delete=False,
        ) as destination:
            temporary_path = Path(destination.name)
            destination.write(contents + "\n")
        os.replace(temporary_path, path)
    except OSError as error:
        raise StorageError(f"Could not save store data at {path}: {error}") from error
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                # Preserve the original save error if cleanup also fails.
                pass
