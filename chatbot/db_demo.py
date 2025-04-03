import sqlite3
import random
import string

# Connect to the database
conn = sqlite3.connect("supply_chain.db", check_same_thread=False)
cursor = conn.cursor()

# Generate random product names
def random_product_name():
    return "Product_" + "".join(random.choices(string.ascii_uppercase, k=5))

# Generate dummy inventory records
inventory_data = [(random_product_name(), random.randint(10, 500), round(random.uniform(10, 1000), 2)) for _ in range(100)]
cursor.executemany("INSERT INTO inventory (product_name, stock, price) VALUES (?, ?, ?)", inventory_data)

# Generate random order IDs
def random_order_id():
    return "ORD" + "".join(random.choices(string.digits, k=6))

# Generate random order status
order_statuses = ["Pending", "Shipped", "Delivered", "Cancelled"]

# Generate dummy orders records
order_data = [(random_order_id(), random.choice(inventory_data)[0], random.choice(order_statuses)) for _ in range(100)]
cursor.executemany("INSERT INTO orders (order_id, product_name, status) VALUES (?, ?, ?)", order_data)

# Commit and close the connection
conn.commit()
conn.close()

print("100 dummy records added to inventory and orders tables successfully!")
