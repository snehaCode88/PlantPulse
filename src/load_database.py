import pandas as pd
import sqlite3
import os

# ============================================================
# PLANTPULSE - LOAD DATA INTO SQL DATABASE
# ============================================================

print("============================================")
print("       PLANTPULSE DATABASE SETUP")
print("============================================")


# ------------------------------------------------------------
# 1. DATABASE LOCATION
# ------------------------------------------------------------

database_path = "data/plantpulse.db"


# ------------------------------------------------------------
# 2. CONNECT TO SQLITE DATABASE
# ------------------------------------------------------------

connection = sqlite3.connect(database_path)

print("\nConnected to SQLite database.")


# ------------------------------------------------------------
# 3. LOAD CSV FILES
# ------------------------------------------------------------

production = pd.read_csv("data/production.csv")
downtime = pd.read_csv("data/downtime.csv")
quality = pd.read_csv("data/quality.csv")
energy = pd.read_csv("data/energy.csv")


# ------------------------------------------------------------
# 4. LOAD DATA INTO SQL TABLES
# ------------------------------------------------------------

production.to_sql(
    "production",
    connection,
    if_exists="replace",
    index=False
)

downtime.to_sql(
    "downtime",
    connection,
    if_exists="replace",
    index=False
)

quality.to_sql(
    "quality",
    connection,
    if_exists="replace",
    index=False
)

energy.to_sql(
    "energy",
    connection,
    if_exists="replace",
    index=False
)


# ------------------------------------------------------------
# 5. CHECK TABLES
# ------------------------------------------------------------

cursor = connection.cursor()

cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type='table'
""")

tables = cursor.fetchall()

print("\nTables created:")

for table in tables:
    print("-", table[0])


# ------------------------------------------------------------
# 6. CHECK NUMBER OF RECORDS
# ------------------------------------------------------------

print("\nRecord counts:")

for table in ["production", "downtime", "quality", "energy"]:

    cursor.execute(
        f"SELECT COUNT(*) FROM {table}"
    )

    count = cursor.fetchone()[0]

    print(f"{table}: {count:,}")


# ------------------------------------------------------------
# 7. CLOSE DATABASE
# ------------------------------------------------------------

connection.close()

print("\nDatabase created successfully!")
print(f"Location: {database_path}")

print("\n============================================")
print("       DATABASE SETUP COMPLETE")
print("============================================")