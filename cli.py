# main.py
# This is the execution layer.
# No fluff. No mercy. Everything wired, validated, and testable.

from product import Product
from inventory import Inventory


def seed_data(inventory):
    inventory.add_product(Product("P1001", "Laptop", "Electronics", 10, 1200))
    inventory.add_product(Product("P1002", "Mouse", "Electronics", 50, 25))
    inventory.add_product(Product("P1003", "Keyboard", "Electronics", 30, 75))
    inventory.add_product(Product("P1004", "Desk Chair", "Furniture", 15, 180))
    inventory.add_product(Product("P1005", "Notebook", "Stationery", 200, 3.5))


def print_products(products):
    if not products:
        print("No products found.")
        return
    for p in products:
        print(p)


def menu():
    print("\nINVENTORY MANAGEMENT SYSTEM")
    print("1. Add product")
    print("2. Remove product")
    print("3. Update stock")
    print("4. Update price")
    print("5. Search by ID")
    print("6. Search by name")
    print("7. Search by category")
    print("8. List products sorted by price")
    print("9. Price range search")
    print("0. Exit")


def main():
    inventory = Inventory()
    seed_data(inventory)

    while True:
        menu()
        choice = input("Select option: ").strip()

        try:
            if choice == "1":
                pid = input("Product ID: ")
                name = input("Name: ")
                category = input("Category: ")
                qty = int(input("Quantity: "))
                price = float(input("Price: "))

                inventory.add_product(Product(pid, name, category, qty, price))
                print("Product added.")

            elif choice == "2":
                pid = input("Product ID: ")
                inventory.remove_product(pid)
                print("Product removed.")

            elif choice == "3":
                pid = input("Product ID: ")
                delta = int(input("Stock change (+/-): "))
                inventory.update_stock(pid, delta)
                print("Stock updated.")

            elif choice == "4":
                pid = input("Product ID: ")
                price = float(input("New price: "))
                inventory.update_price(pid, price)
                print("Price updated.")

            elif choice == "5":
                pid = input("Product ID: ")
                product = inventory.get_by_id(pid)
                print(product if product else "Product not found.")

            elif choice == "6":
                name = input("Search name: ")
                print_products(inventory.search_by_name(name))

            elif choice == "7":
                category = input("Category: ")
                print_products(inventory.search_by_category(category))

            elif choice == "8":
                order = input("Descending order? (y/n): ").lower() == "y"
                print_products(inventory.list_sorted_by_price(reverse=order))

            elif choice == "9":
                low = float(input("Min price: "))
                high = float(input("Max price: "))
                print_products(inventory.price_range(low, high))

            elif choice == "0":
                print("Exiting.")
                break

            else:
                print("Invalid option.")

        except Exception as e:
            print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
