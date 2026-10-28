# Grocery Store Management System

A menu-driven Python terminal application for managing a grocery store's
products, customers, and sales. This project is being built one milestone at a
time using regular functions, modules, lists, and dictionaries.

## Current progress

**Milestone 1: project foundation.** The menu and JSON storage are implemented.
Options 1-7 currently explain which upcoming milestone will introduce the
operation. Option 8 exits the application.

| Milestone | Scope | Status |
| --- | --- | --- |
| 1 | Repository setup, menu, JSON storage, initial tests and documentation | Complete |
| 2 | Add, update, and display products; validate IDs, prices, and stock | Planned |
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
- The file is loaded at startup. Future feature modules will save after each
  successful change, so records remain available after restarting.
- The data path is relative to `storage.py`, so starting the application from
  another working directory still uses the same file.
- Saves write to a temporary file before replacing the existing JSON file.
  Products, customers, and sales are saved together.
- Invalid JSON, invalid collection structures, and file access errors are
  reported. An existing invalid file is not silently reset or overwritten.
- Storage currently validates collection structure. Each feature milestone
  will add validation for individual record fields and business rules.

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
|-- storage.py               # JSON validation, loading, and saving
|-- data/
|   |-- store.example.json   # Empty example tracked in Git
|   `-- store.json           # Created locally at runtime; ignored by Git
|-- tests/
|   |-- test_main.py         # Menu and startup behavior
|   `-- test_storage.py      # Persistence and failure handling
|-- .gitignore
|-- LICENSE
`-- README.md
```

`products.py`, `customers.py`, and `sales.py` will be added as we implement
their respective milestones.

## Run the tests

From the project directory:

```sh
python -m unittest discover -s tests -v
```

Use `py` or `python3` instead of `python` if that is your installed command.
Tests use temporary files and do not change actual store records.

Current checks cover first-run file creation, saving and reloading records,
malformed or unreadable data, invalid saves, failed file replacement, menu
repetition, upcoming options, and clean exits.

## Planned business rules

- Product IDs and customer IDs must be unique within their own collections.
- Product and customer names and IDs cannot be blank.
- Prices must be positive; stock quantities must be nonnegative whole numbers.
- A sale requires an existing customer and product, a positive whole-number
  quantity, and sufficient stock.
- Successful sales receive unique sale IDs, calculate the total, and reduce
  stock. Failed sales leave records unchanged.
- A later product price change must preserve totals already recorded in sales.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
