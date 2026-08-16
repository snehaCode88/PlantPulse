import sqlite3

# Connect to PlantPulse database
connection = sqlite3.connect("data/plantpulse.db")

cursor = connection.cursor()

# ============================================================
# STEP 17 - M-05 QUALITY IMPACT
# ============================================================

query = """
WITH p05_total AS (
    SELECT
        SUM(Defective_Units) AS Total_P05_Defects
    FROM quality
    WHERE Product = 'P-05'
),

m05_data AS (
    SELECT
        SUM(Units_Produced) AS M05_Units_Produced,
        SUM(Defective_Units) AS M05_Defective_Units
    FROM quality
    WHERE Product = 'P-05'
      AND Machine = 'M-05'
)

SELECT
    M05_Units_Produced,
    M05_Defective_Units,

    ROUND(
        M05_Defective_Units * 100.0
        / M05_Units_Produced,
        2
    ) AS M05_Defect_Rate,

    ROUND(
        M05_Defective_Units * 100.0
        / Total_P05_Defects,
        2
    ) AS Share_of_P05_Defects

FROM m05_data, p05_total;
"""

# Execute query
cursor.execute(query)

result = cursor.fetchone()

# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n============================================")
print("       M-05 QUALITY IMPACT")
print("============================================")

print(f"\nP-05 units produced by M-05:")
print(f"{result[0]:,.0f}")

print(f"\nP-05 defective units from M-05:")
print(f"{result[1]:,.0f}")

print(f"\nM-05 defect rate:")
print(f"{result[2]:.2f}%")

print(f"\nM-05 share of ALL P-05 defects:")
print(f"{result[3]:.2f}%")

print("\n============================================")

connection.close()