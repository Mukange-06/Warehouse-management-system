import json
import os
from pathlib import Path
from product import Product


DEFAULT_DB_DIR = Path(__file__).parent
DEFAULT_DB_FILE = DEFAULT_DB_DIR / 'inventory.json'


def _ensure_dir(path: Path):
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)


def save_inventory(inventory, file_path: str | Path = DEFAULT_DB_FILE):
    """Save inventory snapshot to a JSON file atomically."""
    file_path = Path(file_path)
    _ensure_dir(file_path)

    data = inventory.snapshot()

    temp_path = file_path.with_suffix('.tmp')
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    os.replace(temp_path, file_path)


def load_inventory(inventory, file_path: str | Path = DEFAULT_DB_FILE):
    """Load inventory from JSON file into the provided Inventory instance.

    Existing inventory items are preserved; duplicates are skipped.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return 0

    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return 0

    loaded = 0
    for item in data:
        try:
            # support both 'product_id' and 'id' keys
            pid = item.get('product_id') or item.get('id')
            if pid is None:
                continue

            product = Product(
                product_id=str(pid),
                name=str(item.get('name', '')),
                category=str(item.get('category', '')),
                quantity=int(item.get('quantity', 0)),
                price=float(item.get('price', 0.0))
            )
            try:
                inventory.add_product(product)
            except Exception:
                # skip duplicates or invalid entries
                continue
            loaded += 1
        except Exception:
            continue

    return loaded
