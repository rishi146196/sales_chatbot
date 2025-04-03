import sqlite3

conn = sqlite3.connect("supply_chain.db")
cursor = conn.cursor()

cursor.execute("SELECT order_id, product_name, status FROM orders")
orders = cursor.fetchall()

if orders:
    for order in orders:
        print(f"Order ID: {order[0]}, Product: {order[1]}, Status: {order[2]}")
else:
    print("❌ No orders found in the table.")

conn.close()
