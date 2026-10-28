"""Record purchases, calculate exact totals, and display sales transactions."""

from decimal import Decimal, localcontext

from customers import get_customer
from products import get_product, normalize_price, normalize_quantity
from validation import normalize_text


def normalize_sale_quantity(value):
    """Return a positive whole-number quantity suitable for a purchase."""
    message = "Quantity purchased must be a positive whole number."
    try:
        quantity = normalize_quantity(value)
    except ValueError as error:
        raise ValueError(message) from error
    if quantity == 0:
        raise ValueError(message)
    return quantity


def calculate_total(price, quantity):
    """Multiply an exact two-place price by a positive integer without rounding."""
    unit_price = Decimal(normalize_price(price))
    quantity = normalize_sale_quantity(quantity)
    with localcontext() as context:
        # Allow enough digits even for amounts beyond Decimal's default precision.
        context.prec = max(28, len(unit_price.as_tuple().digits) + len(str(quantity)) + 2)
        return format(unit_price * quantity, ".2f")


def next_sale_id(sales):
    """Choose the first unused ID in the sequence S001, S002, and so on."""
    existing_ids = {sale["sale_id"] for sale in sales}
    number = 1
    while f"S{number:03d}" in existing_ids:
        number += 1
    return f"S{number:03d}"


def record_sale(store, customer_id, product_id, quantity):
    """Validate a purchase, append its sale, and reduce stock together in memory.

    Invalid purchases leave the store untouched. The menu calls this function
    on a draft and accepts that draft only after saving the whole JSON file.
    """
    customer_id = normalize_text(customer_id, "Customer ID")
    product_id = normalize_text(product_id, "Product ID")
    get_customer(store["customers"], customer_id)
    product = get_product(store["products"], product_id)
    quantity = normalize_sale_quantity(quantity)
    if quantity > product["quantity"]:
        raise ValueError(f"Insufficient stock: only {product['quantity']} units available.")

    sale = {
        "sale_id": next_sale_id(store["sales"]),
        "customer_id": customer_id,
        "product_id": product_id,
        "quantity": quantity,
        "total_price": calculate_total(product["price"], quantity),
    }
    product["quantity"] -= quantity
    store["sales"].append(sale)
    return sale


def validate_sales(sales, products, customers):
    """Check saved transaction fields, unique IDs, and existing references.

    Historical totals and quantities are not compared with today's price or
    stock: later price changes and earlier sales may have changed both.
    """
    seen_ids = set()
    fields = {"sale_id", "customer_id", "product_id", "quantity", "total_price"}
    for sale in sales:
        if not isinstance(sale, dict) or set(sale) != fields:
            raise ValueError("Each sale must contain its ID, customer ID, product ID, quantity, and total price.")
        for field in ("sale_id", "customer_id", "product_id"):
            if normalize_text(sale[field], field.replace("_", " ").capitalize()) != sale[field]:
                raise ValueError("Stored sale IDs and references cannot have surrounding whitespace.")
        if sale["sale_id"] in seen_ids:
            raise ValueError(f"Duplicate sale ID '{sale['sale_id']}'.")
        seen_ids.add(sale["sale_id"])
        get_customer(customers, sale["customer_id"])
        get_product(products, sale["product_id"])
        if isinstance(sale["quantity"], bool) or not isinstance(sale["quantity"], int):
            raise ValueError("Sale quantities must be stored as positive integers.")
        normalize_sale_quantity(sale["quantity"])
        normalize_price(sale["total_price"])


def display_sales(sales):
    """Print every transaction with its recorded total and identifying fields."""
    if not sales:
        print("No sales recorded. Choose option 6 to record a sale.")
        return

    print("\nSales transactions")
    print(f"{'Sale ID':<12} {'Customer ID':<14} {'Product ID':<14} {'Quantity':>8} {'Total':>14}")
    print("-" * 66)
    for sale in sales:
        total = normalize_price(sale["total_price"])
        print(f"{sale['sale_id']:<12} {sale['customer_id']:<14} {sale['product_id']:<14} "
              f"{sale['quantity']:>8} {total:>14}")
