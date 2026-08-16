import pandas as pd
import numpy as np
import os

# ============================================================
# PLANTPULSE - MANUFACTURING DATA GENERATOR
# ============================================================

np.random.seed(42)

# ------------------------------------------------------------
# 1. BASIC INFORMATION
# ------------------------------------------------------------

plants = ["Plant A", "Plant B", "Plant C"]

machines = ["M-01", "M-02", "M-03", "M-04", "M-05"]

products = ["P-01", "P-02", "P-03", "P-04", "P-05", "P-06"]

shifts = ["Morning", "Evening", "Night"]

downtime_reasons = [
    "Mechanical Failure",
    "Electrical Failure",
    "Maintenance",
    "Material Shortage",
    "Changeover",
    "Operator Issue"
]

# Six months of data
dates = pd.date_range(
    start="2026-01-01",
    end="2026-06-30",
    freq="D"
)

# ------------------------------------------------------------
# 2. CREATE DATA ROWS
# ------------------------------------------------------------

production_data = []
downtime_data = []
quality_data = []
energy_data = []

for date in dates:

    for plant in plants:

        for machine in machines:

            for shift in shifts:

                # Randomly select a product
                product = np.random.choice(products)

                # ------------------------------------------------
                # BASE PRODUCTION
                # ------------------------------------------------

                target = np.random.randint(750, 1200)

                # Night shift performs slightly worse
                if shift == "Night":
                    production_factor = 0.88
                elif shift == "Evening":
                    production_factor = 0.96
                else:
                    production_factor = 1.00

                # ------------------------------------------------
                # HIDDEN PROBLEM #1:
                # Plant B / M-04 has unusually high downtime
                # ------------------------------------------------

                if plant == "Plant B" and machine == "M-04":
                    downtime_hours = np.random.uniform(4.0, 8.0)
                else:
                    downtime_hours = np.random.uniform(0.2, 3.5)

                # Production loss caused by downtime
                downtime_impact = downtime_hours * np.random.uniform(
                    25, 45
                )

                actual = (
                    target * production_factor
                    - downtime_impact
                    + np.random.normal(0, 25)
                )

                actual = max(0, int(actual))

                # ------------------------------------------------
                # DOWNTIME REASON
                # ------------------------------------------------

                if plant == "Plant B" and machine == "M-04":

                    reason = np.random.choice(
                        downtime_reasons,
                        p=[0.45, 0.20, 0.10, 0.05, 0.10, 0.10]
                    )

                else:

                    reason = np.random.choice(
                        downtime_reasons
                    )

                # ------------------------------------------------
                # HIDDEN PROBLEM #2:
                # Product P-05 has higher defect rate
                # ------------------------------------------------

                if product == "P-05":
                    defect_rate = np.random.uniform(0.045, 0.085)
                else:
                    defect_rate = np.random.uniform(0.008, 0.035)

                defective_units = int(
                    actual * defect_rate
                )

                # ------------------------------------------------
                # HIDDEN PROBLEM #3:
                # M-03 consumes more energy
                # ------------------------------------------------

                if machine == "M-03":
                    energy_per_unit = np.random.uniform(0.75, 0.90)
                else:
                    energy_per_unit = np.random.uniform(0.45, 0.65)

                energy = actual * energy_per_unit

                # ------------------------------------------------
                # STORE PRODUCTION DATA
                # ------------------------------------------------

                production_data.append([
                    date,
                    plant,
                    machine,
                    product,
                    shift,
                    target,
                    actual
                ])

                # ------------------------------------------------
                # STORE DOWNTIME DATA
                # ------------------------------------------------

                downtime_data.append([
                    date,
                    plant,
                    machine,
                    downtime_hours,
                    reason
                ])

                # ------------------------------------------------
                # STORE QUALITY DATA
                # ------------------------------------------------

                quality_data.append([
                    date,
                    plant,
                    machine,
                    product,
                    actual,
                    defective_units
                ])

                # ------------------------------------------------
                # STORE ENERGY DATA
                # ------------------------------------------------

                energy_data.append([
                    date,
                    plant,
                    machine,
                    energy
                ])


# ============================================================
# 3. CONVERT TO DATAFRAMES
# ============================================================

production_df = pd.DataFrame(
    production_data,
    columns=[
        "Date",
        "Plant",
        "Machine",
        "Product",
        "Shift",
        "Target_Production",
        "Actual_Production"
    ]
)

downtime_df = pd.DataFrame(
    downtime_data,
    columns=[
        "Date",
        "Plant",
        "Machine",
        "Downtime_Hours",
        "Downtime_Reason"
    ]
)

quality_df = pd.DataFrame(
    quality_data,
    columns=[
        "Date",
        "Plant",
        "Machine",
        "Product",
        "Units_Produced",
        "Defective_Units"
    ]
)

energy_df = pd.DataFrame(
    energy_data,
    columns=[
        "Date",
        "Plant",
        "Machine",
        "Energy_kWh"
    ]
)


# ============================================================
# 4. SAVE DATA
# ============================================================

os.makedirs("data", exist_ok=True)

production_df.to_csv(
    "data/production.csv",
    index=False
)

downtime_df.to_csv(
    "data/downtime.csv",
    index=False
)

quality_df.to_csv(
    "data/quality.csv",
    index=False
)

energy_df.to_csv(
    "data/energy.csv",
    index=False
)


# ============================================================
# 5. DISPLAY RESULTS
# ============================================================

print()
print("============================================")
print("       PLANTPULSE DATA GENERATION")
print("============================================")

print(
    f"Production records : {len(production_df):,}"
)

print(
    f"Downtime records   : {len(downtime_df):,}"
)

print(
    f"Quality records    : {len(quality_df):,}"
)

print(
    f"Energy records     : {len(energy_df):,}"
)

print()
print("CSV files created successfully!")
print("============================================")