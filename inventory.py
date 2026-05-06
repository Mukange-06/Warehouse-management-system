# inventory.py
# This is the brain of the system.
# If this file is sloppy, the entire project is cosplay.

from product import Product
from hash_table import HashTable
from bst import BST


class Inventory:
    def __init__(self, table_size=211):
        # Prime size reduces collisions — basics matter
        self._products = HashTable(table_size)
        self._price_index = BST()
        self._count = 0

    # ---------- CORE OPERATIONS ----------

    def add_product(self, product: Product):
        if not isinstance(product, Product):
            raise TypeError("Only Product instances can be added")

        if self._products.get(product.product_id) is not None:
            raise ValueError(f"Product ID '{product.product_id}' already exists")

        self._products.insert(product.product_id, product)
        self._price_index.insert(product.price, product.product_id)
        self._count += 1

    def remove_product(self, product_id: str):
        product = self._products.get(product_id)
        if product is None:
            raise KeyError(f"Product ID '{product_id}' not found")

        self._products.delete(product_id)
        self._price_index.delete(product.price, product_id)
        self._count -= 1

    def update_stock(self, product_id: str, delta: int):
        product = self._products.get(product_id)
        if product is None:
            raise KeyError(f"Product ID '{product_id}' not found")

        product.update_quantity(delta)

    def update_price(self, product_id: str, new_price: float):
        product = self._products.get(product_id)
        if product is None:
            raise KeyError(f"Product ID '{product_id}' not found")

        # Remove old price index entry
        self._price_index.delete(product.price, product.product_id)

        product.update_price(new_price)

        # Insert updated price
        self._price_index.insert(product.price, product.product_id)

    # ---------- SEARCHING ----------

    def get_by_id(self, product_id: str):
        return self._products.get(product_id)

    # Backwards-compatible alias used by API
    def get_product(self, product_id: str):
        return self.get_by_id(product_id)

    # Allow iteration over product IDs (used by API list endpoints)
    def __iter__(self):
        for bucket in self._products.table:
            for key, _ in bucket:
                yield key
    def search_by_name(self, name: str):
        if not isinstance(name, str):
            raise TypeError("name must be a string")

        name = name.lower()
        results = []

        for bucket in self._products.table:
            for _, product in bucket:
                if name in product.name.lower():
                    results.append(product)

        return results

    def search_by_category(self, category: str):
        if not isinstance(category, str):
            raise TypeError("category must be a string")

        category = category.lower()
        results = []

        for bucket in self._products.table:
            for _, product in bucket:
                if product.category.lower() == category:
                    results.append(product)

        return results

    # ---------- SORTING & RANGE QUERIES ----------

    def list_sorted_by_price(self, reverse=False):
        ordered = self._price_index.inorder()
        products = [self._products.get(pid) for _, pid in ordered]

        if reverse:
            products.reverse()

        return products

    def price_range(self, low: float, high: float):
        if low > high:
            raise ValueError("low must be <= high")

        ids = self._price_index.range_search(low, high)
        return [self._products.get(pid) for pid in ids]

    # ---------- METRICS & DEBUG ----------

    def total_products(self):
        return self._count

    def is_empty(self):
        return self._count == 0

    def snapshot(self):
        # Brutally honest dump of internal state (debugging gold)
        data = []
        for bucket in self._products.table:
            for _, product in bucket:
                data.append(product.to_dict())
        return data

    def __len__(self):
        return self._count

    def __str__(self):
        return f"Inventory(total_products={self._count})"
