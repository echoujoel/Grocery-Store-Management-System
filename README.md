# Grocery Store Management System

A Python terminal application for managing grocery store inventory, registering
customers, and recording sales. It uses ordinary functions and modules,
dictionaries for products and customers, and a list for sales transactions.
Records are saved to JSON so they remain available after the program closes.

The workflow is to add products, register customers, record their purchases,
and review inventory and sales. Every successful purchase calculates a total
and reduces the available stock.

## Installation and startup

You need **Python 3.10 or newer** and a terminal. Git is needed only to clone
the repository. The application uses the Python standard library, so there
are no additional packages to install.

Clone the repository and enter its directory:

```sh
git clone https://github.com/echoujoel/Grocery-Store-Management-System.git
cd Grocery-Store-Management-System
```

Alternatively, download the repository as a ZIP, extract it, and open a terminal
in the folder containing `main.py`.

Check your Python version and start the application:

```sh
python --version
python main.py
```

On Windows, you can use `py` if the Python launcher is configured. On Linux
or macOS, your command may be `python3`. Use the same command when running tests.
If `python` is not recognized or opens the Microsoft Store, use the full path
to your installed interpreter. In PowerShell, prefix a quoted path with `&`:

```powershell
& "C:\path\to\python.exe" main.py
```

## Main menu

At startup, the application loads existing records or creates an empty store.
It displays this menu and repeats it after each operation:

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

Enter an option and press Enter. Invalid choices produce a helpful message
and return you to the menu.

## Complete workflow

The following example follows one product and customer through the application.
Use a fresh copy to reproduce it exactly, since these IDs may already exist
in a store you have used before.

### 1. Add inventory

Choose **option 1** and enter:

```text
Product ID: P001
Product name: Rice
Price (for example, 5000 or 12.50): 5000
Quantity in stock: 20
Product 'P001' added and saved.
```

Choose **option 3** to see the product's ID, name, price, and stock quantity.
A duplicate ID is rejected without replacing the existing product.

### 2. Update a product

Choose **option 2**, enter `P001`, and change the name to `Brown rice`, the price
to `5500`, and stock to `15`. Option 3 will show Brown rice at `5500.00` with
15 units available.

Each update prompt shows the current value. Press Enter to keep that value,
or enter a replacement. Entering `0` sets stock to zero. The product ID stays
fixed, and keeping every field unchanged skips the save.

### 3. Register a customer

Choose **option 4** and enter:

```text
Customer ID: C001
Customer name: Joel
Email address: joel@example.com
Customer 'C001' registered and saved.
```

Choose **option 5** to view customer IDs, names, and email addresses. Customer
IDs must be unique within their collection. Email addresses may be shared;
they do not serve as customer IDs.

### 4. Record a purchase

Choose **option 6** and enter the registered customer, an existing product,
and the quantity purchased:

```text
Customer ID: C001
Product ID: P001
Brown rice: price 5500.00, stock 15.
Quantity purchased: 3
Sale 'S001' recorded and saved. Total: 16500.00
```

The program calculates `5500.00 × 3 = 16500.00`, records the sale, and reduces
stock from 15 to 12. Sale IDs are generated automatically using the first
unused ID in the sequence `S001`, `S002`, and so on, including after a restart.

A purchase is rejected if either ID does not exist, the quantity is invalid,
or stock is insufficient. Both inventory and sales remain unchanged. Buying
all remaining units is allowed; replenish stock through option 2 before
recording another purchase of that product.

### 5. Review store records

Use the reporting options whenever you need to check the store:

| Option | Records displayed |
| --- | --- |
| 3 | Product ID, name, price, and stock quantity |
| 5 | Customer ID, name, and email address |
| 7 | Sale ID, customer ID, product ID, quantity sold, and total price |

After the example purchase, option 3 shows 12 units of `P001`. Option 7 lists
`S001`, `C001`, `P001`, quantity `3`, and total `16500.00`. Sales appear in
transaction order. Empty collections display guidance on adding a first record.

Changing a product's price later affects future purchases while preserving
the totals already recorded in sales.

### 6. Exit and resume

Choose **option 8** to exit. Ctrl+C during menu input or record entry also exits;
an incomplete entry is discarded. Successful changes have already been saved,
so there is no separate save command.

Run `python main.py` again to load the same products, customers, stock levels,
and sales history and continue working.

## Validation rules

| Field | Rule |
| --- | --- |
| Product and customer IDs | Required, trimmed, case-sensitive, and unique within their own collections |
| Product and customer names | Required; surrounding whitespace is removed |
| Product price | Positive, with up to two decimal places, such as `5000` or `12.50` |
| Stock quantity | A whole number of zero or more |
| Purchase quantity | A positive whole number that does not exceed available stock |
| Email address | A common ASCII format, such as `joel@example.com` or `joel.smith+shop@example.co.ug` |

Use a consistent ID convention, such as `P001` and `C001`. `P001` and `p001` are
different IDs. Enter prices without currency symbols, thousands separators,
or exponent notation, and use the same currency throughout the store.

Email checks reject missing parts, spaces, consecutive dots, and invalid domain
labels. The domain is lowercased while the part before `@` keeps its case.
Validation checks format rather than whether an address exists, and does not
support every specialized email format.

Invalid input produces an explanation and returns to the menu. Updates are
accepted together, so one invalid field prevents a partial product update.

## JSON storage and backups

The program creates `data/store.json` on its first run and loads it on subsequent
starts. Products and customers are dictionaries keyed by ID; sales are stored
in a list. After the example workflow, the file contains:

```json
{
  "products": {
    "P001": {
      "name": "Brown rice",
      "price": "5500.00",
      "quantity": 12
    }
  },
  "customers": {
    "C001": {
      "name": "Joel",
      "email": "joel@example.com"
    }
  },
  "sales": [
    {
      "sale_id": "S001",
      "customer_id": "C001",
      "product_id": "P001",
      "quantity": 3,
      "total_price": "16500.00"
    }
  ]
}
```

Prices and totals are saved as decimal strings and processed with Python's
`Decimal` type to preserve exact amounts. The data path is relative to the
source code, so starting from another working directory uses the same file.

Each successful change saves all collections together. A temporary file is
written before replacing the existing JSON file, and success is confirmed only
after saving. A failed save leaves active records and the existing file
unchanged, keeping a sale and its stock reduction together.

Malformed JSON, duplicate keys, invalid records, and access errors produce
messages rather than silently resetting or overwriting existing files. If
startup fails, preserve the file and restore a valid backup before trying again.

To back up records, close the application and copy `data/store.json` somewhere
safe. To restore them, close the application and replace the file with a known
valid backup. Run one application instance at a time.

The repository includes an empty `data/store.example.json`. Actual store data
is ignored by Git, keeping customer details and transactions out of the source
repository.

## Project structure

```text
Grocery-Store-Management-System/
|-- main.py                  # Menu, prompts, and application entry point
|-- products.py              # Product validation, updates, and inventory display
|-- customers.py             # Customer validation, registration, and listings
|-- sales.py                 # Transactions, exact totals, and sales history
|-- storage.py               # JSON validation, loading, and saving
|-- validation.py            # Shared required-text validation
|-- data/
|   |-- store.example.json   # Empty storage example tracked in Git
|   `-- store.json           # Created locally; ignored by Git
|-- tests/                   # Function, menu, storage, and terminal tests
|-- TESTING.md               # Test report and demonstration checklist
|-- README.md
|-- .gitignore
`-- LICENSE
```

## Testing

Run the automated tests from the project directory:

```sh
python -m unittest discover -s tests -v
```

The verified result is **84 tests passed on Windows with Python 3.14.7**.
Checks cover successful operations, invalid inputs, duplicate IDs, unavailable
stock, exact totals, failed saves, malformed files, and persistence. Five
acceptance tests launch the actual program in temporary copies to verify
complete workflows and process restarts. Real store records are untouched.

See [TESTING.md](TESTING.md) for requirements coverage, the test scope, and a
repeatable manual demonstration. Python 3.10 or newer is the target; other
versions and operating systems have not been verified in this environment.

## Submission and scope

Submit the complete source folder, including all six Python modules, `tests/`,
this README, `TESTING.md`, `data/store.example.json`, and the license. A fresh
copy creates its own empty store file, so leave actual `data/store.json`
records out of the submission.

The application covers the assignment's terminal-based inventory, customer,
sales, and reporting requirements. Each sale records one product. Customer
editing, record deletion, currency conversion, and multiple simultaneous users
are outside the current scope.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
