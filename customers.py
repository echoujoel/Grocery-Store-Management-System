"""Register, validate, and display customer records with ordinary functions."""

import re

from validation import normalize_text


def normalize_email(value):
    """Check a common ASCII email format and lowercase its domain.

    This is a basic format check. It does not contact an email provider or
    confirm that the address exists. Names and IDs may still contain Unicode.
    """
    email = normalize_text(value, "Email address")
    message = "Enter an email address like name@example.com."
    if len(email) > 254 or email.count("@") != 1:
        raise ValueError(message)
    local, domain = email.split("@")
    if len(local) > 64 or not re.fullmatch(
        r"[A-Za-z0-9_%+-]+(?:\.[A-Za-z0-9_%+-]+)*", local
    ):
        raise ValueError(message)
    labels = domain.split(".")
    if len(labels) < 2 or any(
        not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", label)
        for label in labels
    ):
        raise ValueError(message)
    return f"{local}@{domain.lower()}"


def validate_customers(customers):
    """Check required fields in customer dictionaries loaded from JSON."""
    for customer_id, customer in customers.items():
        if normalize_text(customer_id, "Customer ID") != customer_id:
            raise ValueError("Stored customer IDs cannot have surrounding whitespace.")
        if not isinstance(customer, dict) or set(customer) != {"name", "email"}:
            raise ValueError(f"Customer {customer_id} must contain name and email.")
        normalize_text(customer["name"], "Customer name")
        normalize_email(customer["email"])


def get_customer(customers, customer_id):
    """Find a registered customer by a trimmed, case-sensitive ID."""
    customer_id = normalize_text(customer_id, "Customer ID")
    if customer_id not in customers:
        raise ValueError(f"Customer '{customer_id}' does not exist.")
    return customers[customer_id]


def register_customer(customers, customer_id, name, email):
    """Register a unique ID only after all customer fields pass validation."""
    customer_id = normalize_text(customer_id, "Customer ID")
    if customer_id in customers:
        raise ValueError(f"Customer ID '{customer_id}' already exists.")
    customer = {
        "name": normalize_text(name, "Customer name"),
        "email": normalize_email(email),
    }
    customers[customer_id] = customer


def display_customers(customers):
    """Print each registered customer's ID, name, and email address."""
    if not customers:
        print("No registered customers. Choose option 4 to register a customer.")
        return

    print("\nRegistered customers")
    print(f"{'ID':<12} {'Name':<24} Email")
    print("-" * 65)
    for customer_id, customer in customers.items():
        print(f"{customer_id:<12} {customer['name']:<24} {customer['email']}")
