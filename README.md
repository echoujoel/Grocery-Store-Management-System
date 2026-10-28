# Grocery Store Management System

A menu-driven Python terminal application for managing a grocery store's
products, customers, and sales. This project is being built one milestone at a
time using regular functions, modules, lists, and dictionaries.

## Current progress

**Milestone 3: customer management.** You can manage products with options 1-3,
register customers with option 4, and view customers with option 5. Successful
changes are saved to JSON and loaded when you restart. Options 6-7 explain the
upcoming sales milestone. Option 8 exits.

| Milestone | Scope | Status |
| --- | --- | --- |
| 1 | Repository setup, menu, JSON storage, initial tests and documentation | Complete |
| 2 | Add, update, and display products; validate IDs, prices, and stock | Complete |
| 3 | Register and display customers; validate IDs, names, and email | Complete |
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
to add one. Sales operations will follow in Milestone 4.

## Manage customers

### Register a customer (option 4)

Enter a unique customer ID, name, and email address. For example:

```text
Customer ID: C001
Customer name: Joel
Email address: joel@example.com
Customer 'C001' registered and saved.
```

- IDs, names, and email addresses are trimmed and cannot be blank.
- Customer IDs are case-sensitive, like product IDs. `C001` and `c001` are
  different IDs. A duplicate ID is rejected without replacing a customer.
- Customer IDs and product IDs belong to separate collections.
- Email validation checks common ASCII formats such as `joel@example.com`
  and `joel.smith+shop@example.co.ug`. It rejects missing parts, spaces,
  consecutive dots, and invalid domain labels. It does not confirm that an
  address exists or support every specialized email format.
- The email domain is lowercased; the part before `@` keeps its case.
- Email addresses may be shared by customers; uniqueness applies to IDs.
- Registration is confirmed only after saving. Invalid input, interrupted
  entry, or a save failure leaves the current store records unchanged.

### View customers (option 5)

The customer list shows every registered customer's ID, name, and email
address. If there are no customers, the application explains how to register
one. Customer changes and deletion are outside the assignment's requirements.

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
- The file is loaded at startup. Product additions, product updates, and customer
  registrations save after validation, so records remain available after restarting.
- The data path is relative to `storage.py`, so starting the application from
  another working directory still uses the same file.
- Saves write to a temporary file before replacing the existing JSON file.
  Products, customers, and sales are saved together.
- Invalid JSON, invalid collection structures, and file access errors are
  reported. An existing invalid file is not silently reset or overwritten.
- Storage validates collection structure, product fields, and customer fields.
  Sales field validation will be added in Milestone 4.

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

Inside the `customers` collection, each customer uses its ID as the key:

```json
{
  "C001": {
    "name": "Joel",
    "email": "joel@example.com"
  }
}
```

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
|-- customers.py             # Customer validation, registration, and listings
|-- validation.py            # Required-text validation shared by feature modules
|-- storage.py               # JSON validation, loading, and saving
|-- data/
|   |-- store.example.json   # Empty example tracked in Git
|   `-- store.json           # Created locally at runtime; ignored by Git
|-- tests/
|   |-- test_main.py         # Menu and startup behavior
|   |-- test_customers.py    # Customer registration and validation
|   |-- test_products.py     # Product operations and rejected changes
|   `-- test_storage.py      # Persistence and failure handling
|-- .gitignore
|-- LICENSE
`-- README.md
```

`sales.py` will be added in Milestone 4.

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
application restart. Customer checks cover registration, duplicate IDs, email
formats, invalid stored records, failed saves, interrupted entry, customer
listings, and persistence while preserving existing products and sales.

## Business rules and remaining work

- Implemented: unique product IDs, required product names and IDs, positive
  prices, and nonnegative whole-number stock quantities.
- Implemented: unique customer IDs, required customer names, and basic email
  format validation.
- A sale requires an existing customer and product, a positive whole-number
  quantity, and sufficient stock.
- Successful sales receive unique sale IDs, calculate the total, and reduce
  stock. Failed sales leave records unchanged.
- A later product price change must preserve totals already recorded in sales.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
