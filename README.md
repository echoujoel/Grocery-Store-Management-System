# Grocery Store Management System

A menu-driven Python terminal application for managing a grocery store's
products, customers, and sales. This project is being built one milestone at a
time using regular functions, modules, lists, and dictionaries.

## Current progress

**Milestone 2: product management.** You can add, update, and view products
through options 1-3. Successful changes are saved to JSON and loaded when you
restart. Options 4-7 explain their upcoming milestones. Option 8 exits.

| Milestone | Scope | Status |
| --- | --- | --- |
| 1 | Repository setup, menu, JSON storage, initial tests and documentation | Complete |
| 2 | Add, update, and display products; validate IDs, prices, and stock | Complete |
| 3 | Register and display customers; validate IDs, names, and email | Planned |
| 4 | Record and display sales; calculate totals and update stock safely | Planned |
| 5 | Test the complete workflow, unsuccessful transactions, and final documentation | Planned |

Each completed milestone will be tested, committed, and pushed to GitHub.

## Requirements

- Python 3.10 or newer.
- A terminal such as PowerShell, Command Prompt, or a Linux/macOS shell.
- Git if you want to clone the repository.

Only the Python standard library is used. No additional packages are required.

## Get started

Clone the repository and enter its directory:

```sh
git clone https://github.com/echoujoel/Grocery-Store-Management-System.git
cd Grocery-Store-Management-System
```

Run the application:

```sh
python main.py
```

On Windows, you can use `py main.py` if your Python installation provides the
Python launcher. On Linux/macOS, the command may be `python3 main.py`.
Check that your selected command reports Python 3.10 or newer with `--version`.

The menu is:

```text
1. Add a product
2. Update a product
3. View all products
4. Register a customer
5. View all customers
6. Record a sale
7. View all sales
8. Exit the application
```

Enter an option and press Enter. Invalid choices display a message and return
to the menu. You can exit with option 8 or Ctrl+C.

## Manage products

### Add a product (option 1)

Enter a unique product ID, name, price, and stock quantity. For example:

```text
Product ID: P001
Product name: Rice
Price (for example, 5000 or 12.50): 5000
Quantity in stock: 20
Product 'P001' added and saved.
```

- IDs and names are trimmed and cannot be blank.
- IDs are case-sensitive: `P001` and `p001` are different IDs. Use a consistent
  convention, such as `P001`, `P002`, and so on.
- Prices must be positive, with up to two decimal places. Enter `5000` or
  `12.50`, without currency symbols, thousands separators, or exponent notation.
- Stock must be a whole number of zero or more; an out-of-stock product can
  have zero units. Fractional quantities are rejected.
- A duplicate ID is rejected without overwriting the existing product.

### Update a product (option 2)

Enter an existing ID, then change its name, price, or stock. Press Enter at
any field to keep its existing value. Enter `0` to set stock to zero. The ID
stays fixed so future sales can continue referring to the same product.

If you keep all existing values, the application reports that no changes were
made. Invalid fields reject the entire update. A save error leaves both the
active inventory and the existing JSON records unchanged.

### View products (option 3)

The inventory lists each product's ID, name, price with two decimal places,
and quantity in stock. If there are no products, the application explains how
to add one. Customer and sales operations will follow in later milestones.

## JSON storage

On the first run, the application creates `data/store.json` with this structure:

```json
{
  "products": {},
  "customers": {},
  "sales": []
}
```

- Products and customers are dictionaries keyed by their unique IDs.
- Sales are stored as a list of transaction dictionaries.
- The file is loaded at startup. Product additions and updates save immediately
  after successful validation, so records remain available after restarting.
- The data path is relative to `storage.py`, so starting the application from
  another working directory still uses the same file.
- Saves write to a temporary file before replacing the existing JSON file.
  Products, customers, and sales are saved together.
- Invalid JSON, invalid collection structures, and file access errors are
  reported. An existing invalid file is not silently reset or overwritten.
- Storage validates collection structure and product fields. Customer and
  sales field validation will be added in their respective milestones.

Inside the `products` collection, each product uses its ID as the dictionary key:

```json
{
  "P001": {
    "name": "Rice",
    "price": "5000.00",
    "quantity": 20
  }
}
```

New prices are stored as decimal strings and validated with Python's `Decimal`
type to preserve exact amounts. Numeric prices from the foundation's initial
storage examples are also accepted when valid. All prices in a store should
use the same currency; currency conversion is outside this project's scope.

`data/store.example.json` is a committed empty example. Actual `data/store.json`
records are ignored by Git to keep local customer and transaction data out of
the repository.

Use one running application instance at a time. Concurrent editing is outside
this project's scope. To back up your records, close the application and copy
`data/store.json` somewhere safe. To restore a backup, close the application and
replace that file with a known valid copy. If a file is damaged, preserve a copy
before attempting repairs; using the empty example discards the previous
records from the application's view.

## Project files

```text
Grocery-Store-Management-System/
|-- main.py                  # Terminal menu and application entry point
|-- products.py              # Product validation, operations, and inventory display
|-- storage.py               # JSON validation, loading, and saving
|-- data/
|   |-- store.example.json   # Empty example tracked in Git
|   `-- store.json           # Created locally at runtime; ignored by Git
|-- tests/
|   |-- test_main.py         # Menu and startup behavior
|   |-- test_products.py     # Product operations and rejected changes
|   `-- test_storage.py      # Persistence and failure handling
|-- .gitignore
|-- LICENSE
`-- README.md
```

`customers.py` and `sales.py` will be added as we implement their milestones.

## Run the tests

From the project directory:

```sh
python -m unittest discover -s tests -v
```

Use `py` or `python3` instead of `python` if that is your installed command.
Tests use temporary files and do not change actual store records.

Current checks cover first-run file creation, saving and reloading records,
malformed or unreadable data, invalid saves, failed file replacement, menu
repetition, upcoming options, and clean exits. Product checks cover duplicate
IDs, missing records, blank fields, invalid prices and stock, partial updates,
failed saves, interrupted entry, inventory display, and persistence across an
application restart.

## Business rules and remaining work

- Implemented: unique product IDs, required product names and IDs, positive
  prices, and nonnegative whole-number stock quantities.
- Milestone 3 will require unique customer IDs and nonblank customer names,
  with email validation.
- A sale requires an existing customer and product, a positive whole-number
  quantity, and sufficient stock.
- Successful sales receive unique sale IDs, calculate the total, and reduce
  stock. Failed sales leave records unchanged.
- A later product price change must preserve totals already recorded in sales.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
