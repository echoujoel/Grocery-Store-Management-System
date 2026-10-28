# Grocery Store Management System

A menu-driven Python terminal application for managing a grocery store's
products, customers, and sales. This project is being built one milestone at a
time using regular functions, modules, lists, and dictionaries.

## Current progress

**Milestone 5: complete and ready for submission.** All eight menu options are implemented.
You can manage products, register customers, record purchases, and view all
store records. Successful changes are saved to JSON and loaded when you
restart. The final verification passed all 84 tests, including checks that
launch the actual program and restart it in separate processes.

| Milestone | Scope | Status |
| --- | --- | --- |
| 1 | Repository setup, menu, JSON storage, initial tests and documentation | Complete |
| 2 | Add, update, and display products; validate IDs, prices, and stock | Complete |
| 3 | Register and display customers; validate IDs, names, and email | Complete |
| 4 | Record and display sales; calculate totals and update stock safely | Complete |
| 5 | Test the complete workflow, unsuccessful transactions, and final documentation | Complete |

All five milestones have been tested and committed separately to GitHub.

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

If `python` is not recognized or opens the Microsoft Store on Windows, use
the full path to your installed Python executable. In PowerShell, put `&`
before a quoted executable path:

```powershell
& "C:\path\to\python.exe" main.py
```

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
to add one.

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

## Manage sales

### Record a sale (option 6)

First add a product with option 1 and register a customer with option 4.
Use options 3 and 5 to find their IDs. Then enter the customer ID, product ID,
and quantity purchased. For the Rice and Joel examples above:

```text
Customer ID: C001
Product ID: P001
Rice: price 5000.00, stock 20.
Quantity purchased: 3
Sale 'S001' recorded and saved. Total: 15000.00
```

The sale leaves 17 units in stock. Each sale covers one product; choose
option 6 again to record another purchase.

- Both IDs must exist. IDs are trimmed and remain case-sensitive.
- Purchase quantities must be positive whole numbers. Zero, negative,
  fractional, blank, and nonnumeric quantities are rejected.
- A purchase cannot exceed the available stock. Buying the last units is
  allowed and leaves zero stock; further purchases are rejected until restocked.
- Sale IDs are generated automatically using the first unused ID in the
  sequence `S001`, `S002`, and so on. Saved transactions are checked to avoid
  duplicate IDs, including after restarting.
- Totals use exact decimal arithmetic and are saved with two decimal places.
- A sale and its stock reduction are saved together. A rejected purchase or
  save failure leaves both inventory and sales unchanged.
- Later product price changes preserve the totals of earlier sales. Sales
  records are historical; they are not recalculated from the current price.

### View sales (option 7)

The sales list shows sale ID, customer ID, product ID, quantity sold, and total
price in transaction order. If no sales exist, the application explains how
to record one.

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
- The file is loaded at startup. Product additions, product updates, customer
  registrations, and sales save after validation, so records remain available
  after restarting.
- The data path is relative to `storage.py`, so starting the application from
  another working directory still uses the same file.
- Saves write to a temporary file before replacing the existing JSON file.
  Products, customers, and sales are saved together.
- Invalid JSON, invalid collection structures, and file access errors are
  reported. An existing invalid file is not silently reset or overwritten.
- Repeated JSON keys are rejected, including duplicate product or customer
  IDs in a manually edited file, instead of silently discarding earlier records.
- Storage validates all record fields. Sales must have unique IDs, positive
  quantities and totals, and references to existing products and customers.

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

New prices and sale totals are stored as decimal strings and validated with
Python's `Decimal` type to preserve exact amounts. Numeric prices from the initial
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

The `sales` collection is a list of transaction dictionaries:

```json
[
  {
    "sale_id": "S001",
    "customer_id": "C001",
    "product_id": "P001",
    "quantity": 3,
    "total_price": "15000.00"
  }
]
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
|-- sales.py                 # Transactions, exact totals, and sales history
|-- validation.py            # Required-text validation shared by feature modules
|-- storage.py               # JSON validation, loading, and saving
|-- data/
|   |-- store.example.json   # Empty example tracked in Git
|   `-- store.json           # Created locally at runtime; ignored by Git
|-- tests/
|   |-- test_cli.py          # Real terminal processes and complete workflows
|   |-- test_main.py         # Menu and startup behavior
|   |-- test_customers.py    # Customer registration and validation
|   |-- test_products.py     # Product operations and rejected changes
|   |-- test_sales.py        # Sales rules, menu integration, and atomic saving
|   `-- test_storage.py      # Persistence and failure handling
|-- .gitignore
|-- LICENSE
|-- TESTING.md               # Requirements coverage and submission checklist
`-- README.md
```

## Run the tests

From the project directory:

```sh
python -m unittest discover -s tests -v
```

Use `py` or `python3` instead of `python` if that is your installed command.
Tests use temporary files and do not change actual store records.

Current checks cover first-run file creation, saving and reloading records,
malformed or unreadable data, invalid saves, failed file replacement, menu
repetition and clean exits. Product checks cover duplicate
IDs, missing records, blank fields, invalid prices and stock, partial updates,
failed saves, interrupted entry, inventory display, and persistence across an
application restart. Customer checks cover registration, duplicate IDs, email
formats, invalid stored records, failed saves, interrupted entry, customer
listings, and persistence while preserving existing products and sales. Sales
checks cover exact totals, unique IDs, insufficient or zero stock, invalid
quantities and references, failed saves, history display, price changes, and
restoring transactions and stock on restart. All tests use isolated test data.

**Final result:** 84 tests passed on Windows with Python 3.14.7. See
[TESTING.md](TESTING.md) for the requirements checklist, exact test scope,
and a repeatable demonstration. Other Python versions and operating systems
have not been verified in this environment.

## Business rules

- Implemented: unique product IDs, required product names and IDs, positive
  prices, and nonnegative whole-number stock quantities.
- Implemented: unique customer IDs, required customer names, and basic email
  format validation.
- Implemented: a sale requires an existing customer and product, a positive whole-number
  quantity, and sufficient stock.
- Implemented: successful sales receive unique sale IDs, calculate the total, and reduce
  stock. Failed sales leave records unchanged.
- Implemented: later product price changes preserve totals already recorded in sales.

## Submission

Submit the complete source folder, including the README, test files,
`TESTING.md`, and `data/store.example.json`. No package installation is needed.
Do not include actual store records; the application creates `data/store.json`
on its first run.

A local ZIP of the completed commit is available at
`dist/Grocery-Store-Management-System.zip` in the development workspace. It
contains the source, tests, documentation, license, and empty JSON example.
The generated ZIP itself is ignored by Git. For a copy from GitHub, use the
repository's **Code > Download ZIP** option or clone the repository.

The application supports one running instance at a time. Each sale records
one product, and email validation checks common formats rather than delivery.
These scope limits are described in the sections above.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
