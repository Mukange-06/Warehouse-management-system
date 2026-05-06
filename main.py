# main.py
# Backend entry point (NOT CLI)
# Clean separation. No input(). No UI garbage.

from inventory import Inventory
from product import Product

def create_inventory():
    inventory = Inventory()

    # Seed data (same as CLI, reused properly)
    inventory.add_product(Product("P1001", "Laptop", "Electronics", 10, 1200))
    inventory.add_product(Product("P1002", "Mouse", "Electronics", 50, 25))
    inventory.add_product(Product("P1003", "Keyboard", "Electronics", 30, 75))
    inventory.add_product(Product("P1004", "Desk Chair", "Furniture", 15, 180))
    inventory.add_product(Product("P1005", "Notebook", "Stationery", 200, 3.5))

    return inventory


def main():
    inventory = create_inventory()

    # Temporary proof the backend works
    print("Backend running.")
    print("Loaded products:")
    for product in inventory.list_all():
        print(product)

    # Later this is where Flask starts
    # app.run(debug=True)


if __name__ == "__main__":
    main()
