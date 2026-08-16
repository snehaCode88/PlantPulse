import pandas as pd

# ============================================================
# PLANTPULSE - DATA INSPECTION
# ============================================================

print("============================================")
print("        PLANTPULSE DATA INSPECTION")
print("============================================")


# ------------------------------------------------------------
# 1. LOAD THE DATA
# ------------------------------------------------------------

production = pd.read_csv("data/production.csv")
downtime = pd.read_csv("data/downtime.csv")
quality = pd.read_csv("data/quality.csv")
energy = pd.read_csv("data/energy.csv")


# ------------------------------------------------------------
# 2. BASIC INFORMATION
# ------------------------------------------------------------

print("\n--- NUMBER OF ROWS ---")

print("Production:", len(production))
print("Downtime:", len(downtime))
print("Quality:", len(quality))
print("Energy:", len(energy))


# ------------------------------------------------------------
# 3. COLUMN INFORMATION
# ------------------------------------------------------------

print("\n--- PRODUCTION COLUMNS ---")

print(production.columns.tolist())


print("\n--- DOWNTIME COLUMNS ---")

print(downtime.columns.tolist())


print("\n--- QUALITY COLUMNS ---")

print(quality.columns.tolist())


print("\n--- ENERGY COLUMNS ---")

print(energy.columns.tolist())


# ------------------------------------------------------------
# 4. CHECK MISSING VALUES
# ------------------------------------------------------------

print("\n--- MISSING VALUES ---")

print("\nProduction:")
print(production.isnull().sum())

print("\nDowntime:")
print(downtime.isnull().sum())

print("\nQuality:")
print(quality.isnull().sum())

print("\nEnergy:")
print(energy.isnull().sum())


# ------------------------------------------------------------
# 5. SHOW SAMPLE RECORDS
# ------------------------------------------------------------

print("\n--- SAMPLE PRODUCTION DATA ---")

print(production.head())


print("\n--- SAMPLE DOWNTIME DATA ---")

print(downtime.head())


print("\n--- SAMPLE QUALITY DATA ---")

print(quality.head())


print("\n--- SAMPLE ENERGY DATA ---")

print(energy.head())


# ------------------------------------------------------------
# 6. BASIC STATISTICS
# ------------------------------------------------------------

print("\n--- PRODUCTION STATISTICS ---")

print(
    production[
        [
            "Target_Production",
            "Actual_Production"
        ]
    ].describe()
)


print("\n--- DOWNTIME STATISTICS ---")

print(
    downtime[
        [
            "Downtime_Hours"
        ]
    ].describe()
)


print("\n--- QUALITY STATISTICS ---")

print(
    quality[
        [
            "Units_Produced",
            "Defective_Units"
        ]
    ].describe()
)


print("\n--- ENERGY STATISTICS ---")

print(
    energy[
        [
            "Energy_kWh"
        ]
    ].describe()
)


print("\n============================================")
print("        DATA INSPECTION COMPLETE")
print("============================================")