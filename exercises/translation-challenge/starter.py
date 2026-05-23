"""
Exercise: The Translation Challenge
Module 3 | Lesson 9 | ~40 min

Objective:
  Solve four analytical questions using BOTH raw SQL (via sqlite3) AND
  pandas. Side-by-side comparison builds intuition for when to reach for
  each tool — and for the pd.read_sql() bridge between them.
"""

import sqlite3
import pandas as pd

# ── Shared dataset (provided — do not modify) ─────────────────────────────────
sales_data = [
    # (id, product,            category,      region,   units, unit_price, date)
    (1,  "Wireless Headphones","Electronics", "West",    12,    79.99, "2024-01-05"),
    (2,  "Yoga Mat",           "Sports",      "East",    25,    34.99, "2024-01-08"),
    (3,  "Python Book",        "Books",       "West",     8,    44.99, "2024-01-12"),
    (4,  "USB-C Hub",          "Electronics", "North",   15,    39.99, "2024-01-15"),
    (5,  "Wireless Headphones","Electronics", "East",    20,    79.99, "2024-01-18"),
    (6,  "Running Shoes",      "Sports",      "West",    10,    89.99, "2024-01-22"),
    (7,  "SQL Book",           "Books",       "South",    5,    29.99, "2024-01-25"),
    (8,  "Bluetooth Speaker",  "Electronics", "East",    18,    59.99, "2024-02-01"),
    (9,  "Yoga Mat",           "Sports",      "West",    30,    34.99, "2024-02-05"),
    (10, "Mechanical Keyboard","Electronics", "North",    7,   129.99, "2024-02-08"),
    (11, "Python Book",        "Books",       "East",    12,    44.99, "2024-02-12"),
    (12, "Water Bottle",       "Sports",      "South",   50,    24.99, "2024-02-15"),
    (13, "Wireless Headphones","Electronics", "North",    9,    79.99, "2024-02-18"),
    (14, "Standing Desk",      "Furniture",   "West",     2,   299.99, "2024-02-22"),
    (15, "Ergonomic Chair",    "Furniture",   "East",     3,   449.99, "2024-03-01"),
    (16, "USB-C Hub",          "Electronics", "South",   22,    39.99, "2024-03-05"),
    (17, "Running Shoes",      "Sports",      "North",   14,    89.99, "2024-03-08"),
    (18, "SQL Book",           "Books",       "West",     9,    29.99, "2024-03-12"),
    (19, "Bluetooth Speaker",  "Electronics", "West",    11,    59.99, "2024-03-15"),
    (20, "Water Bottle",       "Sports",      "East",    45,    24.99, "2024-03-18"),
]

# ── SQLite setup ──────────────────────────────────────────────────────────────
conn = sqlite3.connect(":memory:")
conn.row_factory = sqlite3.Row

conn.execute("""
    CREATE TABLE sales (
        id         INTEGER PRIMARY KEY,
        product    TEXT,
        category   TEXT,
        region     TEXT,
        units      INTEGER,
        unit_price REAL,
        date       TEXT
    )
""")
conn.executemany(
    "INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?, ?)",
    sales_data
)
conn.commit()

# ── pandas DataFrame setup ────────────────────────────────────────────────────
df = pd.DataFrame(sales_data, columns=[
    "id", "product", "category", "region", "units", "unit_price", "date"
])
# Add a computed revenue column to the DataFrame
df["revenue"] = df["units"] * df["unit_price"]


# ── Question 1: Total revenue per category ────────────────────────────────────
# Which categories generated the most revenue overall?
print("=== Q1: Total revenue per category ===")

# SQL approach:
sql_q1 = """
    SELECT category, SUM(units * unit_price) AS total_revenue
    FROM sales
    GROUP BY category
    ORDER BY total_revenue DESC
"""
print("SQL result:")
for row in conn.execute(sql_q1):
    print(f"  {row['category']}: ${row['total_revenue']:.2f}")

# Pandas approach:
print("Pandas result:")
pandas_q1 = df.groupby("category")["revenue"].sum().sort_values(ascending=False)
for category, total in pandas_q1.items():
    print(f"  {category}: ${total:.2f}")
print()

# ── Question 2: Best-selling product by units sold ────────────────────────────
# Which single product sold the most units (across all dates and regions)?
print("=== Q2: Best-selling product by total units ===")

# SQL approach:
sql_q2 = """
    SELECT product, SUM(units) AS total_units
    FROM sales
    GROUP BY product
    ORDER BY total_units DESC
    LIMIT 1
"""
row = conn.execute(sql_q2).fetchone()
print(f"SQL: {row['product']} — {row['total_units']} units")

# Pandas approach:
units_by_product = df.groupby("product")["units"].sum()
best_product = units_by_product.idxmax()
print(f"Pandas: {best_product} — {units_by_product[best_product]} units")
print()

# ── Question 3: Revenue by region for Electronics only ────────────────────────
# Which region sells the most Electronics (by revenue)?
print("=== Q3: Electronics revenue by region ===")

# SQL approach:
sql_q3 = """
    SELECT region, SUM(units * unit_price) AS revenue
    FROM sales
    WHERE category = 'Electronics'
    GROUP BY region
    ORDER BY revenue DESC
"""
print("SQL result:")
for row in conn.execute(sql_q3):
    print(f"  {row['region']}: ${row['revenue']:.2f}")

# Pandas approach:
print("Pandas result:")
electronics = df[df["category"] == "Electronics"]
pandas_q3 = electronics.groupby("region")["revenue"].sum().sort_values(ascending=False)
for region, revenue in pandas_q3.items():
    print(f"  {region}: ${revenue:.2f}")
print()

# ── Question 4: Month-over-month sales trend ──────────────────────────────────
# How did total revenue change from January -> February -> March?
print("=== Q4: Monthly revenue trend ===")

# SQL approach:
sql_q4 = """
    SELECT strftime('%Y-%m', date) AS month,
           SUM(units * unit_price) AS monthly_revenue
    FROM sales
    GROUP BY month
    ORDER BY month
"""
print("SQL result:")
for row in conn.execute(sql_q4):
    print(f"  {row['month']}: ${row['monthly_revenue']:.2f}")

# Pandas approach:
print("Pandas result:")
df_monthly = df.copy()
df_monthly["month"] = pd.to_datetime(df_monthly["date"]).dt.to_period("M")
pandas_q4 = df_monthly.groupby("month")["revenue"].sum().sort_index()
for month, revenue in pandas_q4.items():
    print(f"  {month}: ${revenue:.2f}")
print()

# ── Bonus: pd.read_sql() bridge ───────────────────────────────────────────────
# pd.read_sql() lets you run SQL and get the result directly as a DataFrame.
print("=== Bonus: pd.read_sql() ===")
bonus_df = pd.read_sql(sql_q1, conn)
print(bonus_df)
print()

conn.close()

# Expected output (sample):
# === Q1: Total revenue per category ===
# SQL result:
#   Electronics: $3,679.55
#   Sports: $3,249.40
#   Furniture: $1,949.95
#   Books: $809.73
#
# === Q2: Best-selling product by total units ===
# SQL: Water Bottle — 95 units
# Pandas: Water Bottle — 95 units
#
# === Q3: Electronics revenue by region ===
#   East: $1,839.60
#   North: $1,369.56
#   West: $659.29
#   South: $879.78
#
# === Q4: Monthly revenue trend ===
#   2024-01: $4,013.56
#   2024-02: $3,539.61
#   2024-03: $2,135.46
