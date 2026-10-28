"""Shared input checks used by the grocery store's feature modules."""


def normalize_text(value, label):
    """Trim a required text field or explain why it is invalid."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} cannot be blank.")
    return value.strip()
