import sqlite3
import pandas as pd


# ============================================================
# CONNECT TO PLANTPULSE DATABASE
# ============================================================

connection = sqlite3.connect(
    "data\plantpulse.db"
)


# ============================================================
# SQL QUERY — PLANT PRODUCTION PERFORMANCE
# ============================================================

query = """
SELECT
    Plant,
    SUM(Target_Production) AS Target_Production,
    SUM(Actual_Production) AS Actual_Production,

    ROUND(
        SUM(Actual_Production) * 100.0
        / NULLIF(SUM(Target_Production), 0),
        2
    ) AS Production_Achievement

FROM production

GROUP BY Plant

ORDER BY Production_Achievement DESC;
"""

# ============================================================
# SQL QUERY — DOWNTIME BY PLANT
# ============================================================

downtime_query = """
SELECT
    Plant,
    SUM(Downtime_Hours) AS Total_Downtime_Hours

FROM downtime

GROUP BY Plant

ORDER BY Total_Downtime_Hours DESC;
"""


# ============================================================
# RUN DOWNTIME QUERY
# ============================================================

downtime_result = pd.read_sql_query(
    downtime_query,
    connection
)


print("\n========================================")
print("DOWNTIME BY PLANT")
print("========================================\n")

print(
    downtime_result.to_string(index=False)
)

# ============================================================
# RUN SQL QUERY
# ============================================================

result = pd.read_sql_query(
    query,
    connection
)


# ============================================================
# DISPLAY RESULT
# ============================================================

print("\n========================================")
print("PLANT PRODUCTION PERFORMANCE")
print("========================================\n")

print(result.to_string(index=False))

# ============================================================
# SQL QUERY — DOWNTIME ROOT CAUSES
# ============================================================

root_cause_query = """
SELECT
    Downtime_Reason,
    SUM(Downtime_Hours) AS Total_Downtime_Hours,

    ROUND(
        SUM(Downtime_Hours) * 100.0
        / NULLIF(
            (SELECT SUM(Downtime_Hours)
             FROM downtime),
            0
        ),
        2
    ) AS Downtime_Share_Percent

FROM downtime

GROUP BY Downtime_Reason

ORDER BY Total_Downtime_Hours DESC;
"""


# ============================================================
# RUN ROOT-CAUSE QUERY
# ============================================================

root_cause_result = pd.read_sql_query(
    root_cause_query,
    connection
)


print("\n========================================")
print("DOWNTIME ROOT-CAUSE ANALYSIS")
print("========================================\n")

print(
    root_cause_result.to_string(index=False)
)
# ============================================================
# SQL QUERY — MACHINE DEFECT ANALYSIS
# ============================================================

machine_defect_query = """
SELECT
    Machine,
    SUM(Units_Produced) AS Total_Units_Produced,
    SUM(Defective_Units) AS Total_Defective_Units,

    ROUND(
        SUM(Defective_Units) * 100.0
        / NULLIF(SUM(Units_Produced), 0),
        2
    ) AS Defect_Rate_Percent

FROM quality

GROUP BY Machine

ORDER BY Defect_Rate_Percent DESC;
"""


# ============================================================
# RUN MACHINE DEFECT QUERY
# ============================================================

machine_defect_result = pd.read_sql_query(
    machine_defect_query,
    connection
)


print("\n========================================")
print("MACHINE DEFECT ANALYSIS")
print("========================================\n")

print(
    machine_defect_result.to_string(index=False)
)
# ============================================================
# SQL QUERY — MONTHLY PRODUCTION TREND
# ============================================================

monthly_production_query = """
SELECT
    strftime('%Y-%m', Date) AS Month,

    SUM(Target_Production) AS Target_Production,

    SUM(Actual_Production) AS Actual_Production,

    ROUND(
        SUM(Actual_Production) * 100.0
        / NULLIF(SUM(Target_Production), 0),
        2
    ) AS Production_Achievement_Percent

FROM production

GROUP BY strftime('%Y-%m', Date)

ORDER BY Month;
"""


# ============================================================
# RUN MONTHLY PRODUCTION QUERY
# ============================================================

monthly_production_result = pd.read_sql_query(
    monthly_production_query,
    connection
)


print("\n========================================")
print("MONTHLY PRODUCTION TREND")
print("========================================\n")

print(
    monthly_production_result.to_string(index=False)
)
# ============================================================
# SQL QUERY — TOP OPERATIONAL PROBLEMS
# ============================================================

top_problems_query = """
WITH plant_production AS (

    SELECT
        Plant,

        SUM(Target_Production) AS Target_Production,

        SUM(Actual_Production) AS Actual_Production,

        ROUND(
            SUM(Actual_Production) * 100.0
            / NULLIF(SUM(Target_Production), 0),
            2
        ) AS Production_Achievement

    FROM production

    GROUP BY Plant
),

plant_downtime AS (

    SELECT
        Plant,

        SUM(Downtime_Hours) AS Total_Downtime_Hours

    FROM downtime

    GROUP BY Plant
),

plant_quality AS (

    SELECT
        Plant,

        SUM(Units_Produced) AS Units_Produced,

        SUM(Defective_Units) AS Defective_Units,

        ROUND(
            SUM(Defective_Units) * 100.0
            / NULLIF(SUM(Units_Produced), 0),
            2
        ) AS Defect_Rate

    FROM quality

    GROUP BY Plant
)

SELECT

    p.Plant,

    p.Production_Achievement,

    d.Total_Downtime_Hours,

    q.Defect_Rate,

    ROUND(
        (100 - p.Production_Achievement)
        + (d.Total_Downtime_Hours / 100.0)
        + (q.Defect_Rate * 5),
        2
    ) AS Operational_Risk_Score

FROM plant_production p

LEFT JOIN plant_downtime d
    ON p.Plant = d.Plant

LEFT JOIN plant_quality q
    ON p.Plant = q.Plant

ORDER BY Operational_Risk_Score DESC;
"""


# ============================================================
# RUN TOP-PROBLEMS QUERY
# ============================================================

top_problems_result = pd.read_sql_query(
    top_problems_query,
    connection
)


print("\n========================================")
print("TOP OPERATIONAL PROBLEMS")
print("========================================\n")

print(
    top_problems_result.to_string(index=False)
)
# ============================================================
# CLOSE DATABASE
# ============================================================

connection.close()