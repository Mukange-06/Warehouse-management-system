# product.py
# This file defines the Product entity.
# If this class is weak, the entire system collapses. So it’s not.

from dataclasses import dataclass, field


@dataclass(order=True)
class Product:
    # The 'order=True' allows comparison/sorting by the first field unless specified
    product_id: str = field(compare=False)
    name: str = field(compare=False)
    category: str = field(compare=False)
    quantity: int = field(compare=False)
    price: float

    def __post_init__(self):
        # Hard validation — silent failures are amateur hour
        if not self.product_id or not isinstance(self.product_id, str):
            raise ValueError("product_id must be a non-empty string")

        if not self.name or not isinstance(self.name, str):
            raise ValueError("name must be a non-empty string")

        if not self.category or not isinstance(self.category, str):
            raise ValueError("category must be a non-empty string")

        if not isinstance(self.quantity, int) or self.quantity < 0:
            raise ValueError("quantity must be a non-negative integer")

        if not isinstance(self.price, (int, float)) or self.price < 0:
            raise ValueError("price must be a non-negative number")

        # Normalize price to float for consistency
        self.price = float(self.price)

    def update_quantity(self, amount: int):
        # Updates stock safely
        if not isinstance(amount, int):
            raise ValueError("amount must be an integer")

        if self.quantity + amount < 0:
            raise ValueError("stock cannot go below zero")

        self.quantity += amount

    def update_price(self, new_price: float):
        # Explicit price update with validation
        if not isinstance(new_price, (int, float)) or new_price < 0:
            raise ValueError("new_price must be a non-negative number")

        self.price = float(new_price)

    def to_dict(self):
        # Useful for persistence or debugging later
        return {
            "product_id": self.product_id,
            "name": self.name,
            "category": self.category,
            "quantity": self.quantity,
            "price": self.price
        }

    def __str__(self):
        # Clean, readable, and actually useful
        return (
            f"[{self.product_id}] "
            f"{self.name} | "
            f"Category: {self.category} | "
            f"Qty: {self.quantity} | "
            f"Price: ${self.price:.2f}"
        )
