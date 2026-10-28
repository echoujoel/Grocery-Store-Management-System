"""Validate and manage product dictionaries using ordinary Python functions."""

from decimal import Decimal
import re

from validation import normalize_text


def normalize_price(value):
    """Return a positive price as an exact decimal string with two places.

    JSON stores new prices as strings to avoid binary floating-point rounding.
    Ordinary numeric prices from the initial storage example are also accepted.
    """
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise ValueError("Price must be a positive number with up to two decimal places.")
    text = str(value).strip()
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]{1,2})?", text):
        raise ValueError("Price must be a positive number with up to two decimal places.")
    price = Decimal(text)
    if price <= 0:
        raise ValueError("Price must be greater than zero.")
    return format(price, ".2f")


def normalize_quantity(value):
    """Return stock as a nonnegative integer; reject fractions and booleans."""
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise ValueError("Stock quantity must be a whole number of zero or more.")
    text = str(value).strip()
    if not re.fullmatch(r"[0-9]+", text):
        raise ValueError("Stock quantity must be a whole number of zero or more.")
    try:
        return int(text)
    except ValueError as error:
        raise ValueError("Stock quantity is too large.") from error


def validate_products(products):
    """Reject invalid product records loaded from JSON or passed for saving."""
    for product_id, product in products.items():
        if normalize_text(product_id, "Product ID") != product_id:
            raise ValueError("Stored product IDs cannot have surrounding whitespace.")
        if not isinstance(product, dict) or set(product) != {"name", "price", "quantity"}:
            raise ValueError(f"Product {product_id} must contain name, price, and quantity.")
        normalize_text(product["name"], "Product name")
        normalize_price(product["price"])
        if isinstance(product["quantity"], bool) or not isinstance(product["quantity"], int):
            raise ValueError(f"Product {product_id} stock must be stored as an integer.")
        normalize_quantity(product["quantity"])


def get_product(products, product_id):
    """Find an existing product by its trimmed, case-sensitive ID."""
    product_id = normalize_text(product_id, "Product ID")
    if product_id not in products:
        raise ValueError(f"Product '{product_id}' does not exist.")
    return products[product_id]


def add_product(products, product_id, name, price, quantity):
    """Add a unique product only after all fields pass validation."""
    product_id = normalize_text(product_id, "Product ID")
    if product_id in products:
        raise ValueError(f"Product ID '{product_id}' already exists.")
    product = {
        "name": normalize_text(name, "Product name"),
        "price": normalize_price(price),
        "quantity": normalize_quantity(quantity),
    }
    products[product_id] = product


def update_product(products, product_id, name=None, price=None, quantity=None):
    """Update fields together, keeping any field passed as None.

    The product ID stays fixed. Return whether the record changed. Invalid
    input leaves the original record untouched, even if other fields are valid.
    """
    product_id = normalize_text(product_id, "Product ID")
    current = get_product(products, product_id)
    updated = {
        "name": current["name"] if name is None else normalize_text(name, "Product name"),
        "price": current["price"] if price is None else normalize_price(price),
        "quantity": current["quantity"] if quantity is None else normalize_quantity(quantity),
    }
    if updated == current:
        return False
    products[product_id] = updated
    return True


def display_products(products):
    """Print each product's ID, name, price, and available stock."""
    if not products:
        print("No products in inventory. Choose option 1 to add a product.")
        return

    print("\nProduct inventory")
    print(f"{'ID':<12} {'Name':<24} {'Price':>12} {'Stock':>8}")
    print("-" * 59)
    for product_id, product in products.items():
        price = normalize_price(product["price"])
        print(f"{product_id:<12} {product['name']:<24} {price:>12} {product['quantity']:>8}")
