"""Run the grocery store's menu-driven terminal application."""

from storage import StorageError, load_store


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
    "1": "Adding products will be available in Milestone 2.",
    "2": "Updating products will be available in Milestone 2.",
    "3": "Viewing products will be available in Milestone 2.",
    "4": "Customer registration will be available in Milestone 3.",
    "5": "Viewing customers will be available in Milestone 3.",
    "6": "Recording sales will be available in Milestone 4.",
    "7": "Viewing sales will be available in Milestone 4.",
}


def display_menu():
    """Show the eight operations required by the project."""
    print(MENU)


def main():
    """Load the store and repeat the menu until the user exits.

    Return a nonzero exit status if the store cannot be loaded safely.
    Feature operations will be connected during their respective milestones.
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
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return 0

        if choice == "8":
            print("Goodbye!")
            return 0
        if choice in UPCOMING_FEATURES:
            print(UPCOMING_FEATURES[choice])
        else:
            print("Invalid choice. Please enter a number from 1 to 8.")


if __name__ == "__main__":
    raise SystemExit(main())
