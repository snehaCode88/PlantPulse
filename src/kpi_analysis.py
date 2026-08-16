import sqlite3

# ============================================================
# PLANTPULSE - DYNAMIC KPI ENGINE
# ============================================================

# Connect to database
connection = sqlite3.connect("data/plantpulse.db")

cursor = connection.cursor()


# ============================================================
# 1. FIND THE WORST-PERFORMING PLANT
# ============================================================

production_query = """
SELECT
    Plant,
    SUM(Target_Production) AS Total_Target,
    SUM(Actual_Production) AS Total_Actual,
    ROUND(
        SUM(Actual_Production) * 100.0
        / SUM(Target_Production),
        2
    ) AS Achievement_Percent
FROM production
GROUP BY Plant
ORDER BY Achievement_Percent ASC
LIMIT 1;
"""

cursor.execute(production_query)

worst_plant = cursor.fetchone()

plant_name = worst_plant[0]
achievement = worst_plant[3]


# ============================================================
# 2. FIND THE BIGGEST DOWNTIME HOTSPOT
#    INSIDE THE WORST PLANT
# ============================================================

downtime_query = """
SELECT
    Machine,
    Downtime_Reason,
    ROUND(SUM(Downtime_Hours), 2) AS Total_Downtime
FROM downtime
WHERE Plant = ?
GROUP BY Machine, Downtime_Reason
ORDER BY Total_Downtime DESC
LIMIT 1;
"""

cursor.execute(downtime_query, (plant_name,))

downtime_hotspot = cursor.fetchone()

machine_name = downtime_hotspot[0]
downtime_reason = downtime_hotspot[1]
downtime_hours = downtime_hotspot[2]


# ============================================================
# 3. CALCULATE FINANCIAL IMPACT
# ============================================================

units_per_hour = 35
value_per_unit = 50

lost_units = downtime_hours * units_per_hour

estimated_loss = lost_units * value_per_unit


# ============================================================
# 4. FIND THE WORST PRODUCT
# ============================================================

quality_query = """
SELECT
    Product,
    SUM(Units_Produced) AS Units_Produced,
    SUM(Defective_Units) AS Defective_Units,
    ROUND(
        SUM(Defective_Units) * 100.0
        / SUM(Units_Produced),
        2
    ) AS Defect_Rate
FROM quality
GROUP BY Product
ORDER BY Defect_Rate DESC
LIMIT 1;
"""

cursor.execute(quality_query)

worst_product = cursor.fetchone()

product_name = worst_product[0]
defect_rate = worst_product[3]


# ============================================================
# 5. FIND THE MACHINE CONTRIBUTING MOST TO
#    THE WORST PRODUCT'S DEFECTS
# ============================================================

machine_quality_query = """
SELECT
    Machine,
    SUM(Defective_Units) AS Defective_Units,
    ROUND(
        SUM(Defective_Units) * 100.0
        /
        (
            SELECT SUM(Defective_Units)
            FROM quality
            WHERE Product = ?
        ),
        2
    ) AS Defect_Contribution
FROM quality
WHERE Product = ?
GROUP BY Machine
ORDER BY Defect_Contribution DESC
LIMIT 1;
"""

cursor.execute(
    machine_quality_query,
    (product_name, product_name)
)

quality_machine = cursor.fetchone()

quality_machine_name = quality_machine[0]
quality_machine_defects = quality_machine[1]
quality_machine_contribution = quality_machine[2]


# ============================================================
# 6. DISPLAY EXECUTIVE SUMMARY
# ============================================================

print("\n")
print("=" * 65)
print("                    PLANTPULSE")
print("                 KPI EXECUTIVE SUMMARY")
print("=" * 65)


print("\nPRODUCTION PERFORMANCE")
print("-" * 65)

print(f"Worst Plant              : {plant_name}")
print(f"Production Achievement   : {achievement:.2f}%")


print("\nDOWNTIME HOTSPOT")
print("-" * 65)

print(f"Machine                  : {machine_name}")
print(f"Main Cause               : {downtime_reason}")
print(f"Total Downtime           : {downtime_hours:,.2f} hours")


print("\nFINANCIAL IMPACT")
print("-" * 65)

print(f"Estimated Lost Production: {lost_units:,.0f} units")
print(f"Estimated Production Loss: ₹{estimated_loss:,.2f}")


print("\nQUALITY PERFORMANCE")
print("-" * 65)

print(f"Worst Product            : {product_name}")
print(f"Defect Rate              : {defect_rate:.2f}%")


print("\nQUALITY CONTRIBUTION")
print("-" * 65)

print(f"Machine                  : {quality_machine_name}")
print(f"Defective Units          : {quality_machine_defects:,}")
print(f"Share of Product Defects : {quality_machine_contribution:.2f}%")


print("\n" + "=" * 65)
print("                    END OF REPORT")
print("=" * 65)


# Close database
connection.close()