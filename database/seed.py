"""
DataPilot Database Seeder
Populates realistic e-commerce sample data for analytics, aggregations,
time-series revenue trends, customer segmentation, and product performance.
Works with both PostgreSQL and SQLite.
"""

import os
import random
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configurable database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./datapilot.db")

CATEGORIES_DATA = [
    {"category_id": 1, "category_name": "Electronics"},
    {"category_id": 2, "category_name": "Computers & Laptops"},
    {"category_id": 3, "category_name": "Office Supplies"},
    {"category_id": 4, "category_name": "Home & Kitchen"},
    {"category_id": 5, "category_name": "Apparel & Footwear"},
    {"category_id": 6, "category_name": "Sports & Outdoors"},
    {"category_id": 7, "category_name": "Books & Stationery"},
]

PRODUCTS_DATA = [
    # Electronics
    {"product_id": 1, "product_name": "Wireless Noise-Canceling Headphones", "category_id": 1, "price": 249.99, "stock_quantity": 85},
    {"product_id": 2, "product_name": "Smart 4K Ultra HD TV 55-inch", "category_id": 1, "price": 699.00, "stock_quantity": 40},
    {"product_id": 3, "product_name": "Bluetooth Portable Speaker", "category_id": 1, "price": 79.99, "stock_quantity": 120},
    {"product_id": 4, "product_name": "Smart Fitness Watch Pro", "category_id": 1, "price": 199.50, "stock_quantity": 95},
    # Computers
    {"product_id": 5, "product_name": "Ultra-Slim 14-inch Laptop", "category_id": 2, "price": 1099.99, "stock_quantity": 30},
    {"product_id": 6, "product_name": "Ergonomic Mechanical Keyboard", "category_id": 2, "price": 129.00, "stock_quantity": 75},
    {"product_id": 7, "product_name": "Wireless Precision Laser Mouse", "category_id": 2, "price": 59.95, "stock_quantity": 110},
    {"product_id": 8, "product_name": "27-inch 144Hz Gaming Monitor", "category_id": 2, "price": 349.99, "stock_quantity": 50},
    {"product_id": 9, "product_name": "USB-C Dual 4K Docking Station", "category_id": 2, "price": 189.00, "stock_quantity": 60},
    # Office Supplies
    {"product_id": 10, "product_name": "Adjustable Standing Desk Converter", "category_id": 3, "price": 219.00, "stock_quantity": 45},
    {"product_id": 11, "product_name": "Ergonomic High-Back Mesh Chair", "category_id": 3, "price": 329.99, "stock_quantity": 35},
    {"product_id": 12, "product_name": "Heavy-Duty Paper Shredder", "category_id": 3, "price": 89.50, "stock_quantity": 70},
    # Home & Kitchen
    {"product_id": 13, "product_name": "Espresso & Cappuccino Machine", "category_id": 4, "price": 449.00, "stock_quantity": 25},
    {"product_id": 14, "product_name": "Stainless Steel Air Fryer 6Qt", "category_id": 4, "price": 119.99, "stock_quantity": 80},
    {"product_id": 15, "product_name": "Smart Robot Vacuum Cleaner", "category_id": 4, "price": 299.00, "stock_quantity": 55},
    {"product_id": 16, "product_name": "Cold Press Slow Masticating Juicer", "category_id": 4, "price": 159.00, "stock_quantity": 40},
    # Apparel & Footwear
    {"product_id": 17, "product_name": "Performance Running Shoes", "category_id": 5, "price": 135.00, "stock_quantity": 150},
    {"product_id": 18, "product_name": "Waterproof All-Weather Jacket", "category_id": 5, "price": 179.99, "stock_quantity": 90},
    {"product_id": 19, "product_name": "Merino Wool Thermal Sweater", "category_id": 5, "price": 95.00, "stock_quantity": 110},
    {"product_id": 20, "product_name": "Classic Tailored Fit Denim Jeans", "category_id": 5, "price": 69.50, "stock_quantity": 130},
    # Sports & Outdoors
    {"product_id": 21, "product_name": "Lightweight 2-Person Camping Tent", "category_id": 6, "price": 189.95, "stock_quantity": 65},
    {"product_id": 22, "product_name": "Adjustable Dumbbell Set 50lbs", "category_id": 6, "price": 299.99, "stock_quantity": 40},
    {"product_id": 23, "product_name": "Inflatable Stand Up Paddleboard", "category_id": 6, "price": 389.00, "stock_quantity": 25},
    {"product_id": 24, "product_name": "High-Density Foam Yoga Mat", "category_id": 6, "price": 39.99, "stock_quantity": 180},
    # Books & Stationery
    {"product_id": 25, "product_name": "Deep Learning with Python Textbook", "category_id": 7, "price": 54.99, "stock_quantity": 200},
    {"product_id": 26, "product_name": "Hardcover Dot-Grid Executive Journal", "category_id": 7, "price": 24.50, "stock_quantity": 250},
    {"product_id": 27, "product_name": "Modern Data Architecture Guide", "category_id": 7, "price": 49.99, "stock_quantity": 140},
]

CUSTOMERS_DATA = [
    {"customer_id": 1, "name": "Alice Johnson", "email": "alice.j@example.com", "city": "New York", "region": "East", "created_at": "2023-01-15 10:30:00"},
    {"customer_id": 2, "name": "Bob Smith", "email": "bob.smith@example.com", "city": "Los Angeles", "region": "West", "created_at": "2023-02-10 14:15:00"},
    {"customer_id": 3, "name": "Carol Williams", "email": "carol.w@example.com", "city": "Chicago", "region": "Central", "created_at": "2023-03-05 09:45:00"},
    {"customer_id": 4, "name": "David Brown", "email": "david.b@example.com", "city": "Houston", "region": "South", "created_at": "2023-03-22 16:20:00"},
    {"customer_id": 5, "name": "Emma Davis", "email": "emma.d@example.com", "city": "Seattle", "region": "West", "created_at": "2023-04-18 11:00:00"},
    {"customer_id": 6, "name": "Frank Miller", "email": "frank.m@example.com", "city": "Miami", "region": "South", "created_at": "2023-05-02 13:40:00"},
    {"customer_id": 7, "name": "Grace Wilson", "email": "grace.w@example.com", "city": "San Francisco", "region": "West", "created_at": "2023-05-29 15:10:00"},
    {"customer_id": 8, "name": "Henry Moore", "email": "henry.m@example.com", "city": "Boston", "region": "East", "created_at": "2023-06-14 08:30:00"},
    {"customer_id": 9, "name": "Ivy Taylor", "email": "ivy.taylor@example.com", "city": "Atlanta", "region": "South", "created_at": "2023-07-01 17:05:00"},
    {"customer_id": 10, "name": "Jack Anderson", "email": "jack.a@example.com", "city": "Denver", "region": "West", "created_at": "2023-07-20 12:25:00"},
    {"customer_id": 11, "name": "Karen Thomas", "email": "karen.t@example.com", "city": "Austin", "region": "South", "created_at": "2023-08-11 10:50:00"},
    {"customer_id": 12, "name": "Leo Martinez", "email": "leo.m@example.com", "city": "Philadelphia", "region": "East", "created_at": "2023-08-30 14:00:00"},
    {"customer_id": 13, "name": "Mia Robinson", "email": "mia.r@example.com", "city": "Portland", "region": "West", "created_at": "2023-09-12 16:30:00"},
    {"customer_id": 14, "name": "Noah Clark", "email": "noah.c@example.com", "city": "Dallas", "region": "South", "created_at": "2023-10-04 09:15:00"},
    {"customer_id": 15, "name": "Olivia Rodriguez", "email": "olivia.r@example.com", "city": "Minneapolis", "region": "Central", "created_at": "2023-10-25 13:00:00"},
    {"customer_id": 16, "name": "Paul Lewis", "email": "paul.l@example.com", "city": "Phoenix", "region": "West", "created_at": "2023-11-10 11:45:00"},
    {"customer_id": 17, "name": "Quinn Lee", "email": "quinn.lee@example.com", "city": "Detroit", "region": "Central", "created_at": "2023-11-28 15:20:00"},
    {"customer_id": 18, "name": "Rachel Walker", "email": "rachel.w@example.com", "city": "Charlotte", "region": "East", "created_at": "2023-12-15 10:10:00"},
    {"customer_id": 19, "name": "Samuel Hall", "email": "samuel.h@example.com", "city": "San Diego", "region": "West", "created_at": "2024-01-08 14:40:00"},
    {"customer_id": 20, "name": "Tina Allen", "email": "tina.a@example.com", "city": "Indianapolis", "region": "Central", "created_at": "2024-01-26 12:00:00"},
    {"customer_id": 21, "name": "Uma Young", "email": "uma.y@example.com", "city": "Nashville", "region": "South", "created_at": "2024-02-14 09:50:00"},
    {"customer_id": 22, "name": "Victor Hernandez", "email": "victor.h@example.com", "city": "Columbus", "region": "Central", "created_at": "2024-03-02 16:00:00"},
    {"customer_id": 23, "name": "Wendy King", "email": "wendy.k@example.com", "city": "Washington", "region": "East", "created_at": "2024-03-20 11:15:00"},
    {"customer_id": 24, "name": "Xavier Wright", "email": "xavier.w@example.com", "city": "Baltimore", "region": "East", "created_at": "2024-04-10 14:30:00"},
    {"customer_id": 25, "name": "Yasmine Lopez", "email": "yasmine.l@example.com", "city": "San Jose", "region": "West", "created_at": "2024-05-01 10:00:00"},
    {"customer_id": 26, "name": "Zachary Hill", "email": "zachary.h@example.com", "city": "Kansas City", "region": "Central", "created_at": "2024-05-22 15:45:00"},
    {"customer_id": 27, "name": "Amber Scott", "email": "amber.s@example.com", "city": "Las Vegas", "region": "West", "created_at": "2024-06-10 12:10:00"},
    {"customer_id": 28, "name": "Brian Green", "email": "brian.g@example.com", "city": "Pittsburgh", "region": "East", "created_at": "2024-07-04 09:30:00"},
    {"customer_id": 29, "name": "Chloe Adams", "email": "chloe.a@example.com", "city": "Raleigh", "region": "East", "created_at": "2024-07-28 16:50:00"},
    {"customer_id": 30, "name": "Daniel Baker", "email": "daniel.b@example.com", "city": "Tampa", "region": "South", "created_at": "2024-08-15 11:20:00"},
]

def generate_orders_and_items():
    """Generates 120 realistic orders across 14 months with order items and payments."""
    random.seed(42)  # Deterministic seed for reproducible testing
    start_date = datetime(2023, 10, 1)
    end_date = datetime(2024, 11, 20)
    delta_days = (end_date - start_date).days

    orders = []
    order_items = []
    payments = []

    order_item_id = 1
    payment_id = 1

    payment_methods = ["credit_card", "paypal", "bank_transfer", "upi"]
    statuses = ["completed", "completed", "completed", "shipped", "pending", "cancelled"]

    product_lookup = {p["product_id"]: p for p in PRODUCTS_DATA}

    for order_id in range(1, 121):
        customer_id = random.randint(1, len(CUSTOMERS_DATA))
        random_day = random.randint(0, delta_days)
        random_second = random.randint(0, 86400)
        order_date = start_date + timedelta(days=random_day, seconds=random_second)
        status = random.choice(statuses)

        # 1 to 4 distinct items per order
        num_items = random.choices([1, 2, 3, 4], weights=[40, 35, 15, 10])[0]
        chosen_products = random.sample(PRODUCTS_DATA, num_items)

        order_total = Decimal("0.00")

        for prod in chosen_products:
            qty = random.choices([1, 2, 3], weights=[70, 20, 10])[0]
            unit_price = Decimal(str(prod["price"]))
            item_total = unit_price * qty
            order_total += item_total

            order_items.append({
                "order_item_id": order_item_id,
                "order_id": order_id,
                "product_id": prod["product_id"],
                "quantity": qty,
                "unit_price": float(unit_price),
            })
            order_item_id += 1

        orders.append({
            "order_id": order_id,
            "customer_id": customer_id,
            "order_date": order_date.strftime("%Y-%m-%d %H:%M:%S"),
            "order_status": status,
            "total_amount": float(order_total),
        })

        # Payment record
        if status in ["completed", "shipped"]:
            pay_status = "success"
        elif status == "pending":
            pay_status = random.choice(["pending", "success"])
        else:
            pay_status = "failed"

        pay_method = random.choice(payment_methods)
        pay_date = order_date + timedelta(minutes=random.randint(2, 60))

        payments.append({
            "payment_id": payment_id,
            "order_id": order_id,
            "payment_method": pay_method,
            "payment_status": pay_status,
            "payment_date": pay_date.strftime("%Y-%m-%d %H:%M:%S"),
            "amount": float(order_total),
        })
        payment_id += 1

    return orders, order_items, payments

def seed_database(database_url: str = None):
    url = database_url or DATABASE_URL
    print(f"Connecting to database: {url}")
    engine = create_engine(url)

    is_sqlite = "sqlite" in url.lower()

    with engine.begin() as conn:
        if is_sqlite:
            # Create tables in SQLite if not exist
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS categories (
                    category_id INTEGER PRIMARY KEY,
                    category_name TEXT NOT NULL UNIQUE
                );
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY,
                    product_name TEXT NOT NULL,
                    category_id INTEGER REFERENCES categories(category_id),
                    price REAL NOT NULL,
                    stock_quantity INTEGER NOT NULL DEFAULT 0
                );
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    city TEXT NOT NULL,
                    region TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY,
                    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    order_status TEXT NOT NULL DEFAULT 'completed',
                    total_amount REAL NOT NULL DEFAULT 0.0
                );
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS order_items (
                    order_item_id INTEGER PRIMARY KEY,
                    order_id INTEGER NOT NULL REFERENCES orders(order_id),
                    product_id INTEGER NOT NULL REFERENCES products(product_id),
                    quantity INTEGER NOT NULL DEFAULT 1,
                    unit_price REAL NOT NULL
                );
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS payments (
                    payment_id INTEGER PRIMARY KEY,
                    order_id INTEGER NOT NULL REFERENCES orders(order_id),
                    payment_method TEXT NOT NULL,
                    payment_status TEXT NOT NULL DEFAULT 'success',
                    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    amount REAL NOT NULL
                );
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS query_history (
                    id TEXT PRIMARY KEY,
                    question TEXT NOT NULL,
                    generated_sql TEXT,
                    execution_status TEXT NOT NULL DEFAULT 'pending',
                    execution_time_ms REAL DEFAULT 0.0,
                    row_count INTEGER DEFAULT 0,
                    natural_language_explanation TEXT,
                    error_message TEXT,
                    result_columns TEXT,
                    result_preview TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))

        # Clear existing data in child -> parent order
        print("Clearing existing data...")
        conn.execute(text("DELETE FROM payments"))
        conn.execute(text("DELETE FROM order_items"))
        conn.execute(text("DELETE FROM orders"))
        conn.execute(text("DELETE FROM products"))
        conn.execute(text("DELETE FROM categories"))
        conn.execute(text("DELETE FROM customers"))

        print("Inserting Categories...")
        for cat in CATEGORIES_DATA:
            conn.execute(
                text("INSERT INTO categories (category_id, category_name) VALUES (:category_id, :category_name)"),
                cat
            )

        print("Inserting Products...")
        for prod in PRODUCTS_DATA:
            conn.execute(
                text("""
                    INSERT INTO products (product_id, product_name, category_id, price, stock_quantity)
                    VALUES (:product_id, :product_name, :category_id, :price, :stock_quantity)
                """),
                prod
            )

        print("Inserting Customers...")
        for cust in CUSTOMERS_DATA:
            conn.execute(
                text("""
                    INSERT INTO customers (customer_id, name, email, city, region, created_at)
                    VALUES (:customer_id, :name, :email, :city, :region, :created_at)
                """),
                cust
            )

        orders, order_items, payments = generate_orders_and_items()

        print(f"Inserting {len(orders)} Orders...")
        for ord_entry in orders:
            conn.execute(
                text("""
                    INSERT INTO orders (order_id, customer_id, order_date, order_status, total_amount)
                    VALUES (:order_id, :customer_id, :order_date, :order_status, :total_amount)
                """),
                ord_entry
            )

        print(f"Inserting {len(order_items)} Order Items...")
        for item in order_items:
            conn.execute(
                text("""
                    INSERT INTO order_items (order_item_id, order_id, product_id, quantity, unit_price)
                    VALUES (:order_item_id, :order_id, :product_id, :quantity, :unit_price)
                """),
                item
            )

        print(f"Inserting {len(payments)} Payments...")
        for pay in payments:
            conn.execute(
                text("""
                    INSERT INTO payments (payment_id, order_id, payment_method, payment_status, payment_date, amount)
                    VALUES (:payment_id, :order_id, :payment_method, :payment_status, :payment_date, :amount)
                """),
                pay
            )

    print("Database successfully seeded with realistic e-commerce data!")

if __name__ == "__main__":
    seed_database()
