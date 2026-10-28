"""Run the grocery store's menu-driven terminal application."""

from copy import deepcopy

from customers import display_customers, register_customer
from products import add_product, display_products, get_product, update_product
from storage import StorageError, load_store, save_store
from validation import normalize_text


MENU = """
Grocery Store Management System
1. Add a product
2. Update a product
3. View all products
4. Register a customer
5. View all customers
6. Record a sale
7. View all sales
8. Exit the application
"""

UPCOMING_FEATURES = {
    "6": "Recording sales will be available in Milestone 4.",
    "7": "Viewing sales will be available in Milestone 4.",
}


def display_menu():
    """Show the eight operations required by the project."""
    print(MENU)


def add_product_from_input(store):
    """Collect product fields and save a draft before accepting the change."""
    product_id = normalize_text(input("Product ID: "), "Product ID")
    if product_id in store["products"]:
        raise ValueError(f"Product ID '{product_id}' already exists.")
    name = input("Product name: ")
    price = input("Price (for example, 5000 or 12.50): ")
    quantity = input("Quantity in stock: ")

    draft = deepcopy(store)
    add_product(draft["products"], product_id, name, price, quantity)
    save_store(draft)
    print(f"Product '{product_id}' added and saved.")
    return draft


def update_product_from_input(store):
    """Collect optional changes, preserving the ID and saving them together."""
    product_id = normalize_text(input("Product ID to update: "), "Product ID")
    product = get_product(store["products"], product_id)
    print("Press Enter to keep an existing value. The product ID stays the same.")
    name = input(f"Name [{product['name']}]: ").strip() or None
    price = input(f"Price [{product['price']}]: ").strip() or None
    quantity = input(f"Quantity [{product['quantity']}]: ").strip() or None

    draft = deepcopy(store)
    if not update_product(draft["products"], product_id, name, price, quantity):
        print("No changes made.")
        return store
    save_store(draft)
    print(f"Product '{product_id}' updated and saved.")
    return draft


def register_customer_from_input(store):
    """Collect customer details and save them before confirming registration."""
    customer_id = normalize_text(input("Customer ID: "), "Customer ID")
    if customer_id in store["customers"]:
        raise ValueError(f"Customer ID '{customer_id}' already exists.")
    name = input("Customer name: ")
    email = input("Email address: ")

    draft = deepcopy(store)
    register_customer(draft["customers"], customer_id, name, email)
    save_store(draft)
    print(f"Customer '{customer_id}' registered and saved.")
    return draft


def main():
    """Load the store and repeat the menu until the user exits.

    Return a nonzero exit status if the store cannot be loaded safely.
    Product and customer changes are accepted only after a successful JSON save.
    """
    try:
        store = load_store()
    except StorageError as error:
        print(f"Unable to start: {error}")
        print("Check the data file and restore a valid backup before trying again.")
        return 1

    print(
        f"Store loaded: {len(store['products'])} products, "
        f"{len(store['customers'])} customers, {len(store['sales'])} sales."
    )

    while True:
        display_menu()
        try:
            choice = input("Choose an option (1-8): ").strip()
            if choice == "8":
                print("Goodbye!")
                return 0
            if choice == "1":
                store = add_product_from_input(store)
            elif choice == "2":
                store = update_product_from_input(store)
            elif choice == "3":
                display_products(store["products"])
            elif choice == "4":
                store = register_customer_from_input(store)
            elif choice == "5":
                display_customers(store["customers"])
            elif choice in UPCOMING_FEATURES:
                print(UPCOMING_FEATURES[choice])
            else:
                print("Invalid choice. Please enter a number from 1 to 8.")
        except ValueError as error:
            print(f"Invalid input: {error}")
        except StorageError as error:
            print(f"Change was not saved: {error}")
            print("The current store records are unchanged. Check the file and try again.")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return 0


if __name__ == "__main__":
    raise SystemExit(main())
