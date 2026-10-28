# Verification and submission checklist

## Final verification

Verified on **28 October 2026**, using **Python 3.14.7 on Windows**.

```sh
python -m unittest discover -s tests -v
```

**Result: 84 tests passed.** This includes function tests, menu integration
tests, storage failure tests, and five acceptance tests that launch the actual
terminal program in separate Python processes.

The application targets Python 3.10 or newer. The recorded execution above
was on Python 3.14.7; other versions and operating systems have not been
verified in this environment. No third-party packages are required.

All automated checks use temporary data or mocked file operations. Acceptance
tests copy the source into temporary directories and start the public
`main.py` entry point, without changing the real `data/store.json` file.

## Requirements coverage

| Requirement | Implementation | Verification |
| --- | --- | --- |
| Add, update, and display products | `products.py`, menu options 1-3 | `test_products.py`, `test_main.py`, `test_cli.py` |
| Unique product IDs and accurate stock | Product validation and dictionary keys | Duplicate, invalid update, zero stock, and sale tests |
| Register and display customers | `customers.py`, options 4-5 | `test_customers.py`, `test_main.py`, `test_cli.py` |
| Unique customer IDs, required names, and email format | Customer validation | Duplicate IDs, blank fields, and malformed email tests |
| Record a customer/product purchase | `sales.py`, option 6 | Sales function, menu, and acceptance tests |
| Calculate the total and reduce inventory | Exact decimal arithmetic and saved store draft | Successful purchases, decimal amounts, final-unit purchases, and restart tests |
| Reject missing customers/products and insufficient stock | Lookup and quantity checks before mutation | Rejected purchase tests and unchanged-file acceptance test |
| Display every required sales field | `display_sales`, option 7 | Sales output tests and acceptance workflow |
| Repeat the eight-option menu until exit | `main.py` loop, option 8 | Invalid choices, clean exit, interruption, and acceptance tests |
| Use ordinary functions, modules, lists, and dictionaries | Six source modules; dictionaries for products/customers and a list for sales | Source review and complete application tests |
| Keep records after closing the application | `storage.py` and local JSON file | Save/reload tests and separate-process restarts |
| Handle malformed data and file errors | Storage validation and `StorageError` handling | Invalid JSON, encoding, duplicate keys, file access, and replacement failure tests |
| Preserve existing records when an operation fails | Validate first; save a draft before accepting it | Function snapshots, failed-save checks, and byte-for-byte unchanged-file checks |
| Document source and explain how to run | Module/function docstrings and `README.md` | Documentation review and entry-point acceptance tests |

## Automated test files

| File | Focus |
| --- | --- |
| `tests/test_cli.py` | Real processes: all eight options, restart, alternate working directory, unsuccessful operations, sold-out stock, malformed files, and incomplete input |
| `tests/test_products.py` | Product fields, unique IDs, updates, inventory listings, and invalid stored products |
| `tests/test_customers.py` | Customer registration, unique IDs, email formats, listings, and invalid stored customers |
| `tests/test_sales.py` | Transactions, exact totals, stock changes, history, references, IDs, persistence, and failed saves |
| `tests/test_main.py` | Menu routing, prompts, errors, interruptions, and product/customer persistence |
| `tests/test_storage.py` | File creation, JSON validation, duplicate keys, malformed or unreadable files, and protected writes |

Save failures are simulated in isolated tests. They are not reproduced by
changing permissions on the user's actual store file. Ctrl+C is tested through
the menu's `KeyboardInterrupt` handler; it is not sent as a real terminal signal
by the subprocess acceptance tests.

## Manual demonstration

For a repeatable demonstration, extract the submission ZIP into a new folder
and run `python main.py` there. Use a fresh copy so the example IDs do not
conflict with your actual records. Run one application instance at a time.

| Step | Action | Expected result |
| --- | --- | --- |
| 1 | Select 3, 5, and 7 on a fresh store | Helpful empty-inventory, customer, and sales messages |
| 2 | Select 1: `P001`, `Rice`, `5000`, `20` | Product saved with stock 20 |
| 3 | Select 2: `P001`, `Brown rice`, `5500`, `15` | Product updated; stock 15 |
| 4 | Select 4: `C001`, `Joel`, `joel@example.com` | Customer saved |
| 5 | Select 3 and 5 | Product and customer appear with their fields |
| 6 | Try option 1 with `P001`, then option 4 with `C001` | Duplicate IDs rejected before further prompts |
| 7 | Select 6: `C001`, `P001`, `3` | Sale `S001`, total `16500.00`, stock 12 |
| 8 | Select 6: `C001`, `P001`, `13` | Insufficient stock; sale history and stock unchanged |
| 9 | Select 6 with a missing customer or product | Clear error, no transaction |
| 10 | Try purchase quantities `0`, `-1`, and `1.5` | Each rejected; records unchanged |
| 11 | Select 2 for `P001`: blank name, price `6000`, blank stock | Price changes; stock remains 12 |
| 12 | Select 7 | `S001` still has total `16500.00` |
| 13 | Select 8, then run the application again | Product, customer, and sale are loaded |
| 14 | Select 6: `C001`, `P001`, `2` | Sale `S002`, total `12000.00`, stock 10 |
| 15 | Select 7, then 8 | Both sales appear; application exits cleanly |

Malformed-file and save-failure checks are covered by automated tests; there
is no need to damage your actual store file for the demonstration.

## Submission contents

Include the complete source folder with:

- `main.py`, `products.py`, `customers.py`, `sales.py`, `storage.py`, and `validation.py`.
- `README.md` for installation, usage, data format, and limitations.
- `TESTING.md` and `tests/` for verification and demonstration instructions.
- `data/store.example.json`, an empty example of the storage structure.
- The existing MIT `LICENSE` and `.gitignore`.

The local submission ZIP is exported from the completed Git commit. It excludes
actual `data/store.json` records, Python caches, the Git history directory,
and local editor settings. The application creates its own empty data file
on the first run. Check `README.md` for the run and test commands.
