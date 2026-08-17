import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path


# ============================================================
# PLANTPULSE DASHBOARD
# ============================================================

st.set_page_config(
    page_title="PlantPulse",
    page_icon="🏭",
    layout="wide"
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

DATABASE_PATH = DATA_DIR / "plantpulse.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

connection = sqlite3.connect(
    str(DATABASE_PATH),
    check_same_thread=False
)


# ============================================================
# LOAD CSV DATA INTO DATABASE
# ============================================================

production_csv = pd.read_csv(
    DATA_DIR / "production.csv"
)

quality_csv = pd.read_csv(
    DATA_DIR / "quality.csv"
)

downtime_csv = pd.read_csv(
    DATA_DIR / "downtime.csv"
)

energy_csv = pd.read_csv(
    DATA_DIR / "energy.csv"
)


# ============================================================
# CREATE / REFRESH DATABASE TABLES
# ============================================================

production_csv.to_sql(
    "production",
    connection,
    if_exists="replace",
    index=False
)

quality_csv.to_sql(
    "quality",
    connection,
    if_exists="replace",
    index=False
)

downtime_csv.to_sql(
    "downtime",
    connection,
    if_exists="replace",
    index=False
)

energy_csv.to_sql(
    "energy",
    connection,
    if_exists="replace",
    index=False
)

connection.commit()
st.write("DATABASE PATH:", DATABASE_PATH)
st.write("DATABASE EXISTS:", DATABASE_PATH.exists())
st.write("DATA DIRECTORY EXISTS:", DATA_DIR.exists())

st.write("Production CSV columns:", production_csv.columns.tolist())

st.write("Production SQL columns:")
st.dataframe(
    pd.read_sql_query(
        "PRAGMA table_info(production)",
        connection
    )
)

st.write("Production table exists:")
st.write(
    pd.read_sql_query(
        "SELECT name FROM sqlite_master WHERE type='table';",
        connection
    )
)
st.write("Testing production table:")

st.dataframe(
    pd.read_sql_query(
        "SELECT * FROM production LIMIT 5;",
        connection
    )
)
# ============================================================
# LOAD RAW DATA
# ============================================================

production_query = """
SELECT
    Date,
    Plant,
    Target_Production,
    Actual_Production
FROM production;
"""

production_df = pd.read_sql_query(
    production_query,
    connection
)


downtime_query = """
SELECT
    Date,
    Plant,
    Machine,
    Downtime_Hours,
    Downtime_Reason
FROM downtime;
"""

downtime_df = pd.read_sql_query(
    downtime_query,
    connection
)


quality_query = """
SELECT
    Date,
    Plant,
    Machine,
    Product,
    Units_Produced,
    Defective_Units
FROM quality;
"""

quality_df = pd.read_sql_query(
    quality_query,
    connection
)


# ============================================================
# SQL DATABASE CONNECTION
# ============================================================

SQL_DB_PATH = DATABASE_PATH

sql_connection = connection


# ============================================================
# SQL QUERY HELPER
# ============================================================

def run_sql_query(query):

    return pd.read_sql_query(
        query,
        sql_connection
    )
# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🔎 Dashboard Filters")

# ------------------------------------------------------------
# PLANT FILTER
# ------------------------------------------------------------

plant_options = ["All"] + sorted(
    production_df["Plant"].unique().tolist()
)

selected_plant = st.sidebar.selectbox(
    "🏭 Select Plant",
    plant_options
)

# ------------------------------------------------------------
# MACHINE FILTER
# ------------------------------------------------------------

if selected_plant == "All":

    machine_options = sorted(
        downtime_df["Machine"].unique().tolist()
    )

else:

    machine_options = sorted(
        downtime_df[
            downtime_df["Plant"] == selected_plant
        ]["Machine"].unique().tolist()
    )

machine_options = ["All"] + machine_options

selected_machine = st.sidebar.selectbox(
    "⚙️ Select Machine",
    machine_options
)

# ------------------------------------------------------------
# PRODUCT FILTER
# ------------------------------------------------------------

if selected_plant == "All":

    product_options = sorted(
        quality_df["Product"].unique().tolist()
    )

else:

    product_options = sorted(
        quality_df[
            quality_df["Plant"] == selected_plant
        ]["Product"].unique().tolist()
    )

product_options = ["All"] + product_options

selected_product = st.sidebar.selectbox(
    "📦 Select Product",
    product_options
)
# ============================================================
# DATE RANGE FILTER
# ============================================================

st.sidebar.markdown("---")

st.sidebar.subheader("📅 Date Range")

# Convert dates to datetime
production_df["Date"] = pd.to_datetime(production_df["Date"])
downtime_df["Date"] = pd.to_datetime(downtime_df["Date"])
quality_df["Date"] = pd.to_datetime(quality_df["Date"])

# Find overall date range
min_date = min(
    production_df["Date"].min(),
    downtime_df["Date"].min(),
    quality_df["Date"].min()
).date()

max_date = max(
    production_df["Date"].max(),
    downtime_df["Date"].max(),
    quality_df["Date"].max()
).date()

# Date range selector
selected_dates = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)
# Convert selected dates to start and end dates
start_date = selected_dates[0]
end_date = selected_dates[1]
st.markdown("---")

st.subheader("💰 Business Assumptions")

st.caption(
    "Adjust these assumptions to estimate the potential financial impact "
    "of operational losses."
)

cost_per_downtime_hour = st.number_input(
    "Downtime cost per hour (₹)",
    min_value=0,
    value=5000,
    step=500
)

cost_per_defective_unit = st.number_input(
    "Cost per defective unit (₹)",
    min_value=0,
    value=50,
    step=10
)

value_per_missed_unit = st.number_input(
    "Value per missed production unit (₹)",
    min_value=0,
    value=100,
    step=10
)
# ============================================================
# APPLY FILTERS
# ============================================================

filtered_production = production_df.copy()

filtered_downtime = downtime_df.copy()

filtered_quality = quality_df.copy()


# ------------------------------------------------------------
# PLANT FILTER
# ------------------------------------------------------------

if selected_plant != "All":

    filtered_production = filtered_production[
        filtered_production["Plant"] == selected_plant
    ]

    filtered_downtime = filtered_downtime[
        filtered_downtime["Plant"] == selected_plant
    ]

    filtered_quality = filtered_quality[
        filtered_quality["Plant"] == selected_plant
    ]


# ------------------------------------------------------------
# MACHINE FILTER
# ------------------------------------------------------------

if selected_machine != "All":

    filtered_downtime = filtered_downtime[
        filtered_downtime["Machine"] == selected_machine
    ]

    filtered_quality = filtered_quality[
        filtered_quality["Machine"] == selected_machine
    ]


# ------------------------------------------------------------
# PRODUCT FILTER
# ------------------------------------------------------------

if selected_product != "All":

    filtered_quality = filtered_quality[
        filtered_quality["Product"] == selected_product
    ]

# ============================================================
# APPLY DATE FILTER
# ============================================================
# Keep a copy before applying the date filter.
# This allows us to compare the selected period
# with the previous period.

production_before_date = filtered_production.copy()
downtime_before_date = filtered_downtime.copy()
quality_before_date = filtered_quality.copy()

if len(selected_dates) == 2:

    start_date = pd.Timestamp(selected_dates[0])
    end_date = pd.Timestamp(selected_dates[1])

    filtered_production = filtered_production[
        (filtered_production["Date"] >= start_date)
        &
        (filtered_production["Date"] <= end_date)
    ]

    filtered_downtime = filtered_downtime[
        (filtered_downtime["Date"] >= start_date)
        &
        (filtered_downtime["Date"] <= end_date)
    ]

    filtered_quality = filtered_quality[
        (filtered_quality["Date"] >= start_date)
        &
        (filtered_quality["Date"] <= end_date)
    ]
    # ============================================================
# ACTIVE FILTER SUMMARY
# ============================================================

st.sidebar.markdown("---")

st.sidebar.subheader("🔎 Active Filters")

st.sidebar.write(
    f"**Plant:** {selected_plant}"
)

st.sidebar.write(
    f"**Machine:** {selected_machine}"
)

if isinstance(selected_dates, tuple) and len(selected_dates) == 2:

    st.sidebar.write(
        f"**Date:** "
        f"{selected_dates[0]} → {selected_dates[1]}"
    )
# ============================================================
# TITLE
# ============================================================

# ============================================================
# PLANTPULSE HEADER
# ============================================================

st.title("🏭 PlantPulse")

#st.caption(
 #   "Operational Intelligence & Decision Support Dashboard")


st.subheader(
    "Industrial Operations Intelligence Dashboard"
)

st.markdown(
    """
    PlantPulse analyzes production, downtime and quality data
    to identify operational problems and estimate their business impact.
    """
)
st.markdown("---")

# ============================================================
# PRODUCTION KPI
# ============================================================
st.header("📌 Operational Overview")
st.markdown("---")
if len(filtered_production) > 0:

    total_target = filtered_production[
        "Target_Production"
    ].sum()

    total_actual = filtered_production[
        "Actual_Production"
    ].sum()

    achievement = (
        total_actual / total_target * 100
    )

else:

    achievement = 0


# ============================================================
# DOWNTIME KPI
# ============================================================

if len(filtered_downtime) > 0:

    total_downtime = filtered_downtime[
        "Downtime_Hours"
    ].sum()

    downtime_machine = (
        filtered_downtime
        .groupby("Machine")["Downtime_Hours"]
        .sum()
        .idxmax()
    )

else:

    total_downtime = 0
    downtime_machine = "N/A"


# ============================================================
# FINANCIAL IMPACT
# ============================================================

units_per_hour = 35
value_per_unit = 50

lost_units = total_downtime * units_per_hour

estimated_loss = lost_units * value_per_unit


# ============================================================
# QUALITY KPI
# ============================================================

if len(filtered_quality) > 0:

    total_units = filtered_quality[
        "Units_Produced"
    ].sum()

    total_defects = filtered_quality[
        "Defective_Units"
    ].sum()

    defect_rate = (
        total_defects / total_units * 100
    )

    worst_product = (
        filtered_quality
        .groupby("Product")
        .apply(
            lambda x:
            x["Defective_Units"].sum()
            / x["Units_Produced"].sum() * 100
        )
        .idxmax()
    )

else:

    defect_rate = 0
    worst_product = "N/A"
# ============================================================
# PERIOD-OVER-PERIOD COMPARISON
# ============================================================

#st.markdown("---")

st.header("📊 Period Comparison")

if len(selected_dates) == 2:

    start_date = pd.Timestamp(selected_dates[0])
    end_date = pd.Timestamp(selected_dates[1])

    # Length of selected period
    period_length = (end_date - start_date).days + 1

    # Previous period
    previous_end = start_date - pd.Timedelta(days=1)
    previous_start = (
        previous_end - pd.Timedelta(days=period_length - 1)
    )

    # --------------------------------------------------------
    # PREVIOUS PERIOD DATA
    # --------------------------------------------------------

    previous_production = production_before_date[
        (production_before_date["Date"] >= previous_start)
        &
        (production_before_date["Date"] <= previous_end)
    ]

    previous_downtime = downtime_before_date[
        (downtime_before_date["Date"] >= previous_start)
        &
        (downtime_before_date["Date"] <= previous_end)
    ]

    previous_quality = quality_before_date[
        (quality_before_date["Date"] >= previous_start)
        &
        (quality_before_date["Date"] <= previous_end)
    ]

    # --------------------------------------------------------
    # PRODUCTION COMPARISON
    # --------------------------------------------------------

    current_target = filtered_production["Target_Production"].sum()
    current_actual = filtered_production["Actual_Production"].sum()

    previous_target = previous_production["Target_Production"].sum()
    previous_actual = previous_production["Actual_Production"].sum()

    if current_target > 0:
        current_achievement = (
            current_actual / current_target * 100
        )
    else:
        current_achievement = 0

    if previous_target > 0:
        previous_achievement = (
            previous_actual / previous_target * 100
        )
    else:
        previous_achievement = 0

    achievement_change = (
        current_achievement - previous_achievement
    )

    # --------------------------------------------------------
    # DOWNTIME COMPARISON
    # --------------------------------------------------------

    current_downtime = (
        filtered_downtime["Downtime_Hours"].sum()
    )

    previous_downtime_hours = (
        previous_downtime["Downtime_Hours"].sum()
    )

    if previous_downtime_hours > 0:

        downtime_change = (
            (current_downtime - previous_downtime_hours)
            / previous_downtime_hours
            * 100
        )

    else:
        downtime_change = 0

    # --------------------------------------------------------
    # QUALITY COMPARISON
    # --------------------------------------------------------

    current_units = (
        filtered_quality["Units_Produced"].sum()
    )

    current_defects = (
        filtered_quality["Defective_Units"].sum()
    )

    previous_units = (
        previous_quality["Units_Produced"].sum()
    )

    previous_defects = (
        previous_quality["Defective_Units"].sum()
    )

    if current_units > 0:
        current_defect_rate = (
            current_defects / current_units * 100
        )
    else:
        current_defect_rate = 0

    if previous_units > 0:
        previous_defect_rate = (
            previous_defects / previous_units * 100
        )
    else:
        previous_defect_rate = 0

    if previous_defect_rate > 0:

        defect_change = (
            (current_defect_rate - previous_defect_rate)
            / previous_defect_rate
            * 100
        )

    else:
        defect_change = 0

    # --------------------------------------------------------
    # DISPLAY COMPARISON
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Production Achievement",
            f"{current_achievement:.2f}%",
            f"{achievement_change:+.2f} pp"
        )

    with col2:

        st.metric(
            "Downtime",
            f"{current_downtime:,.1f} hrs",
            f"{downtime_change:+.1f}%"
        )

    with col3:

        st.metric(
            "Defect Rate",
            f"{current_defect_rate:.2f}%",
            f"{defect_change:+.1f}%"
        )

    st.caption(
        f"Current period: "
        f"{start_date.date()} → {end_date.date()}  |  "
        f"Previous period: "
        f"{previous_start.date()} → {previous_end.date()}"
    )

else:

    st.info(
        "Select a complete date range to view "
        "period-over-period performance."
    )
    # ============================================================
# TOP 3 OPERATIONAL PROBLEMS
# ============================================================

st.markdown("---")

st.header("🚨 Top 3 Operational Problems")

problems = []

# ------------------------------------------------------------
# PROBLEM 1 — PRODUCTION
# ------------------------------------------------------------

# Calculate plant-level production achievement
plant_production = (
    filtered_production
    .groupby("Plant")
    .agg(
        Target=("Target_Production", "sum"),
        Actual=("Actual_Production", "sum")
    )
)

plant_production["Achievement"] = (
    plant_production["Actual"]
    / plant_production["Target"]
    * 100
)

# Find the worst-performing plant
if len(plant_production) > 0:

    worst_plant = plant_production["Achievement"].idxmin()

    worst_plant_achievement = (
        plant_production.loc[
            worst_plant, "Achievement"
        ]
    )

    production_gap = 100 - worst_plant_achievement

    problems.append({
        "type": "Production",
        "title": f"{worst_plant} — Low Production Achievement",
        "value": f"{worst_plant_achievement:.2f}%",
        "detail": f"{production_gap:.2f}% below the 100% target",
        "priority": production_gap
    })


# ------------------------------------------------------------
# PROBLEM 2 — DOWNTIME
# ------------------------------------------------------------

machine_downtime = (
    filtered_downtime
    .groupby("Machine")["Downtime_Hours"]
    .sum()
    .sort_values(ascending=False)
)

if len(machine_downtime) > 0:

    worst_machine = machine_downtime.index[0]

    worst_machine_downtime = (
        machine_downtime.iloc[0]
    )

    machine_data = filtered_downtime[
        filtered_downtime["Machine"] == worst_machine
    ]

    if len(machine_data) > 0:

        main_reason = (
            machine_data
            .groupby("Downtime_Reason")["Downtime_Hours"]
            .sum()
            .idxmax()
        )

    else:

        main_reason = "Unknown"

    problems.append({
        "type": "Downtime",
        "title": f"{worst_machine} — High Downtime",
        "value": f"{worst_machine_downtime:.1f} hrs",
        "detail": f"Main reason: {main_reason}",
        "priority": worst_machine_downtime
    })


# ------------------------------------------------------------
# PROBLEM 3 — QUALITY
# ------------------------------------------------------------

product_quality = (
    filtered_quality
    .groupby("Product")
    .agg(
        Units=("Units_Produced", "sum"),
        Defects=("Defective_Units", "sum")
    )
)

product_quality["Defect_Rate"] = (
    product_quality["Defects"]
    / product_quality["Units"]
    * 100
)

if len(product_quality) > 0:

    worst_product_top3 = (
        product_quality["Defect_Rate"]
        .idxmax()
    )

    worst_product_rate = (
        product_quality.loc[
            worst_product_top3,
            "Defect_Rate"
        ]
    )

    worst_product_defects = (
        product_quality.loc[
            worst_product_top3,
            "Defects"
        ]
    )

    problems.append({
        "type": "Quality",
        "title": (
            f"{worst_product_top3} — "
            f"High Defect Rate"
        ),
        "value": f"{worst_product_rate:.2f}%",
        "detail": (
            f"{worst_product_defects:,.0f} defective units"
        ),
        "priority": worst_product_rate
    })


# ------------------------------------------------------------
# DISPLAY TOP 3
# ------------------------------------------------------------

for i, problem in enumerate(problems[:3]):

    if i == 0:
        icon = "🥇"
    elif i == 1:
        icon = "🥈"
    else:
        icon = "🥉"

    st.markdown(
        f"### {icon} {i + 1}. {problem['title']}"
    )

    col1, col2 = st.columns([1, 3])

    with col1:

        st.metric(
            problem["type"],
            problem["value"]
        )

    with col2:

        st.write(
            f"**{problem['detail']}**"
        )
        # ============================================================
# MACHINE QUALITY ANALYSIS
# ============================================================

st.markdown("---")

st.header("🔧 Machine Quality Analysis")

# Calculate machine-level production and defects
machine_quality = (
    filtered_quality
    .groupby("Machine")
    .agg(
        Units_Produced=("Units_Produced", "sum"),
        Defective_Units=("Defective_Units", "sum")
    )
)

# Calculate defect rate
machine_quality["Defect_Rate"] = (
    machine_quality["Defective_Units"]
    / machine_quality["Units_Produced"]
    * 100
)

# Sort highest defect rate first
machine_quality = machine_quality.sort_values(
    "Defect_Rate",
    ascending=False
)

# Display the table
st.dataframe(
    machine_quality.style.format({
        "Units_Produced": "{:,.0f}",
        "Defective_Units": "{:,.0f}",
        "Defect_Rate": "{:.2f}%"
    }),
    use_container_width=True
)

# ------------------------------------------------------------
# MACHINE QUALITY ALERT
# ------------------------------------------------------------

if len(machine_quality) > 0:

    worst_machine_quality = machine_quality.index[0]

    worst_machine_rate = machine_quality.iloc[0]["Defect_Rate"]

    worst_machine_defects = (
        machine_quality.iloc[0]["Defective_Units"]
    )

    st.warning(
        f"⚠️ **Quality Investigation Priority: "
        f"{worst_machine_quality}**\n\n"
        f"This machine has the highest defect rate of "
        f"**{worst_machine_rate:.2f}%**, with "
        f"**{worst_machine_defects:,.0f} defective units**.\n\n"
        f"**Recommended action:** Investigate machine "
        f"settings, operating conditions and maintenance "
        f"history for {worst_machine_quality}."
    )
# ============================================================
# DOWNTIME VS PRODUCTION PERFORMANCE
# ============================================================

st.markdown("---")

st.subheader("📉 Downtime vs Production Performance")


# ============================================================
# CREATE PLANT-LEVEL PRODUCTION SUMMARY
# ============================================================

plant_production = (
    filtered_production
    .groupby("Plant", as_index=False)
    .agg(
        Target_Production=("Target_Production", "sum"),
        Actual_Production=("Actual_Production", "sum")
    )
)


plant_production["Achievement"] = (
    plant_production["Actual_Production"]
    * 100.0
    / plant_production["Target_Production"].replace(0, pd.NA)
).round(2)


# ============================================================
# CREATE PLANT-LEVEL DOWNTIME SUMMARY
# ============================================================

plant_downtime = (
    filtered_downtime
    .groupby("Plant", as_index=False)
    .agg(
        Downtime_Hours=("Downtime_Hours", "sum")
    )
)


# ============================================================
# COMBINE PRODUCTION AND DOWNTIME
# ============================================================

downtime_production_result = pd.merge(
    plant_production[
        [
            "Plant",
            "Achievement"
        ]
    ],
    plant_downtime[
        [
            "Plant",
            "Downtime_Hours"
        ]
    ],
    on="Plant",
    how="inner"
)


# ============================================================
# CHECK WHETHER ENOUGH DATA EXISTS
# ============================================================

if len(downtime_production_result) >= 2:

    # --------------------------------------------------------
    # SORT BY DOWNTIME
    # --------------------------------------------------------

    downtime_production_result = (
        downtime_production_result
        .sort_values(
            "Downtime_Hours",
            ascending=True
        )
        .reset_index(drop=True)
    )


    # --------------------------------------------------------
    # DISPLAY SUMMARY TABLE
    # --------------------------------------------------------

    st.dataframe(
        downtime_production_result[
            [
                "Plant",
                "Achievement",
                "Downtime_Hours"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # LINE CHART
    # --------------------------------------------------------

        # --------------------------------------------------------
    # ZOOMED LINE CHART
    # --------------------------------------------------------

    import altair as alt

    y_min = downtime_production_result["Achievement"].min()
    y_max = downtime_production_result["Achievement"].max()

    y_lower = max(0, y_min - 1)
    y_upper = min(100, y_max + 1)

    line_chart = (
        alt.Chart(downtime_production_result)
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "Downtime_Hours:Q",
                title="Downtime Hours"
            ),
            y=alt.Y(
                "Achievement:Q",
                title="Production Achievement (%)",
                scale=alt.Scale(
                    domain=[y_lower, y_upper]
                )
            ),
            tooltip=[
                alt.Tooltip(
                    "Plant:N",
                    title="Plant"
                ),
                alt.Tooltip(
                    "Downtime_Hours:Q",
                    title="Downtime Hours",
                    format=".1f"
                ),
                alt.Tooltip(
                    "Achievement:Q",
                    title="Achievement (%)",
                    format=".2f"
                )
            ]
        )
        .properties(
            height=400
        )
    )

    st.altair_chart(
        line_chart,
        use_container_width=True
    )


    # --------------------------------------------------------
    # CALCULATE CORRELATION
    # --------------------------------------------------------

    correlation = (
        downtime_production_result[
            "Downtime_Hours"
        ]
        .corr(
            downtime_production_result[
                "Achievement"
            ]
        )
    )


    # --------------------------------------------------------
    # DISPLAY CORRELATION
    # --------------------------------------------------------

    st.markdown(
        "#### Downtime vs Production Correlation"
    )


    st.metric(
        "Correlation",
        f"{correlation:.2f}"
    )


    # --------------------------------------------------------
    # INTERPRETATION
    # --------------------------------------------------------

    if correlation <= -0.7:

        st.error(
            f"🔴 **Strong negative relationship detected "
            f"({correlation:.2f})**\n\n"
            f"Plants with higher downtime tend to have "
            f"lower production achievement. Maintenance and "
            f"downtime-related losses should be investigated."
        )


    elif correlation <= -0.4:

        st.warning(
            f"🟠 **Moderate negative relationship detected "
            f"({correlation:.2f})**\n\n"
            f"Higher downtime is associated with lower "
            f"production achievement."
        )


    elif correlation >= 0.4:

        st.info(
            f"🔵 **Positive relationship detected "
            f"({correlation:.2f})**\n\n"
            f"Downtime and production achievement move in "
            f"the same direction in the selected data."
        )


    else:

        st.info(
            f"⚪ **Weak relationship detected "
            f"({correlation:.2f})**\n\n"
            f"The selected plant-level data does not show "
            f"a strong linear relationship between downtime "
            f"and production achievement."
        )

else:

    st.info(
        "Not enough plant-level data is available "
        "to calculate the relationship."
    )
    # ============================================================
# DOWNTIME ROOT CAUSE ANALYSIS
# ============================================================

st.markdown("---")

st.header("🚨 Downtime Root Cause Analysis")

# ------------------------------------------------------------
# CALCULATE DOWNTIME BY REASON
# ------------------------------------------------------------

downtime_reasons = (
    filtered_downtime
    .groupby("Downtime_Reason")["Downtime_Hours"]
    .sum()
    .sort_values(ascending=False)
)

# ------------------------------------------------------------
# CALCULATE SHARE OF TOTAL DOWNTIME
# ------------------------------------------------------------

total_downtime_reason = downtime_reasons.sum()

if total_downtime_reason > 0:

    downtime_share = (
        downtime_reasons
        / total_downtime_reason
        * 100
    )

else:

    downtime_share = downtime_reasons * 0


# ------------------------------------------------------------
# CREATE ANALYSIS TABLE
# ------------------------------------------------------------

downtime_analysis = pd.DataFrame({
    "Downtime_Hours": downtime_reasons,
    "Share_of_Total_%": downtime_share
})

downtime_analysis["Cumulative_%"] = (
    downtime_analysis["Share_of_Total_%"]
    .cumsum()
)


# ------------------------------------------------------------
# DISPLAY TABLE
# ------------------------------------------------------------

st.dataframe(
    downtime_analysis.style.format({
        "Downtime_Hours": "{:,.1f}",
        "Share_of_Total_%": "{:.2f}%",
        "Cumulative_%": "{:.2f}%"
    }),
    use_container_width=True
)
# ------------------------------------------------------------
# PARETO CHART
# ------------------------------------------------------------

if len(downtime_analysis) > 0:

    fig = go.Figure()

    # Downtime bars
    fig.add_trace(
        go.Bar(
            x=downtime_analysis.index,
            y=downtime_analysis["Downtime_Hours"],
            name="Downtime Hours"
        )
    )

    # Cumulative percentage line
    fig.add_trace(
        go.Scatter(
            x=downtime_analysis.index,
            y=downtime_analysis["Cumulative_%"],
            name="Cumulative %",
            yaxis="y2",
            mode="lines+markers"
        )
    )

    # 80% reference line
    fig.add_hline(
        y=80,
        line_dash="dash",
        annotation_text="80% threshold",
        yref="y2"
    )

    fig.update_layout(
        title="Downtime Pareto Analysis",
        xaxis_title="Downtime Reason",
        yaxis_title="Downtime Hours",
        yaxis2=dict(
            title="Cumulative %",
            overlaying="y",
            side="right",
            range=[0, 100]
        ),
        legend=dict(
            orientation="h"
        ),
        height=500
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
# ------------------------------------------------------------
# IDENTIFY MAIN ROOT CAUSE
# ------------------------------------------------------------

if len(downtime_analysis) > 0:

    top_reason = downtime_analysis.index[0]

    top_reason_hours = (
        downtime_analysis.iloc[0]["Downtime_Hours"]
    )

    top_reason_share = (
        downtime_analysis.iloc[0]["Share_of_Total_%"]
    )

    st.warning(
        f"⚠️ **Primary Downtime Driver: {top_reason}**\n\n"
        f"This reason accounts for "
        f"**{top_reason_hours:,.1f} hours** of downtime, "
        f"representing **{top_reason_share:.2f}%** of total "
        f"downtime.\n\n"
        f"**Recommended action:** Prioritize investigation "
        f"and corrective action for **{top_reason}**."
    )

else:

    st.info(
        "No downtime data is available for the selected filters."
    )
# ============================================================
# BUSINESS RECOMMENDATIONS
# ============================================================

st.markdown("---")

st.header("💡 PlantPulse Business Recommendations")

recommendations = []


# ------------------------------------------------------------
# RECOMMENDATION 1 — PRODUCTION
# ------------------------------------------------------------

if len(plant_production) > 0:

    worst_plant_rec = plant_production["Achievement"].idxmin()

    worst_plant_achievement_rec = (
        plant_production.loc[
            worst_plant_rec,
            "Achievement"
        ]
    )

    production_gap_rec = (
        100 - worst_plant_achievement_rec
    )

    if production_gap_rec >= 10:

        recommendations.append({
            "priority": "🔴 HIGH",
            "category": "Production",
            "message": (
                f"**{worst_plant_rec}** is operating "
                f"{production_gap_rec:.2f} percentage points "
                f"below the production target. "
                f"Investigate production losses, capacity "
                f"constraints and operational bottlenecks."
            )
        })

    elif production_gap_rec >= 5:

        recommendations.append({
            "priority": "🟠 MEDIUM",
            "category": "Production",
            "message": (
                f"**{worst_plant_rec}** is operating at "
                f"{worst_plant_achievement_rec:.2f}% of target. "
                f"Investigate the main sources of production "
                f"loss and improve process efficiency."
            )
        })

    else:

        recommendations.append({
            "priority": "🟢 LOW",
            "category": "Production",
            "message": (
                f"Production performance is relatively close "
                f"to target. Continue monitoring **{worst_plant_rec}** "
                f"for emerging performance gaps."
            )
        })


# ------------------------------------------------------------
# RECOMMENDATION 2 — DOWNTIME
# ------------------------------------------------------------

if len(downtime_analysis) > 0:

    top_downtime_reason_rec = downtime_analysis.index[0]

    top_downtime_share_rec = (
        downtime_analysis.iloc[0]["Share_of_Total_%"]
    )

    if top_downtime_share_rec >= 30:

        recommendations.append({
            "priority": "🔴 HIGH",
            "category": "Downtime",
            "message": (
                f"**{top_downtime_reason_rec}** accounts for "
                f"{top_downtime_share_rec:.2f}% of total downtime. "
                f"Prioritize root-cause investigation and "
                f"corrective maintenance for this failure mode."
            )
        })

    elif top_downtime_share_rec >= 20:

        recommendations.append({
            "priority": "🟠 MEDIUM",
            "category": "Downtime",
            "message": (
                f"**{top_downtime_reason_rec}** is the largest "
                f"downtime contributor at "
                f"{top_downtime_share_rec:.2f}%. "
                f"Review maintenance records and operating "
                f"conditions associated with this issue."
            )
        })

    else:

        recommendations.append({
            "priority": "🟢 LOW",
            "category": "Downtime",
            "message": (
                f"**{top_downtime_reason_rec}** is currently "
                f"the largest downtime contributor. "
                f"Continue monitoring this failure category."
            )
        })


# ------------------------------------------------------------
# RECOMMENDATION 3 — QUALITY
# ------------------------------------------------------------

if len(machine_quality) > 0:

    worst_machine_rec = machine_quality.index[0]

    worst_machine_rate_rec = (
        machine_quality.iloc[0]["Defect_Rate"]
    )

    if worst_machine_rate_rec >= 6:

        recommendations.append({
            "priority": "🔴 HIGH",
            "category": "Quality",
            "message": (
                f"**{worst_machine_rec}** has a defect rate "
                f"of {worst_machine_rate_rec:.2f}%, the highest "
                f"among the machines analyzed. Investigate "
                f"machine settings, maintenance history and "
                f"operating conditions."
            )
        })

    elif worst_machine_rate_rec >= 4:

        recommendations.append({
            "priority": "🟠 MEDIUM",
            "category": "Quality",
            "message": (
                f"**{worst_machine_rec}** has the highest "
                f"defect rate at {worst_machine_rate_rec:.2f}%. "
                f"Review its operating parameters and quality "
                f"history."
            )
        })

    else:

        recommendations.append({
            "priority": "🟢 LOW",
            "category": "Quality",
            "message": (
                f"Machine-level defect rates are relatively "
                f"low. Continue monitoring **{worst_machine_rec}** "
                f"as the current highest-rate machine."
            )
        })


# ------------------------------------------------------------
# DISPLAY RECOMMENDATIONS
# ------------------------------------------------------------

if len(recommendations) > 0:

    for recommendation in recommendations:

        st.markdown(
            f"### {recommendation['priority']} — "
            f"{recommendation['category']}"
        )

        st.info(
            recommendation["message"]
        )

else:

    st.success(
        "No major operational issues were identified "
        "for the current filters."
    )
    # ============================================================
# FINANCIAL IMPACT ANALYSIS
# ============================================================

st.markdown("---")

st.header("💰 Estimated Business Impact")

# ------------------------------------------------------------
# BUSINESS ASSUMPTIONS
# ------------------------------------------------------------



# ------------------------------------------------------------
# PRODUCTION LOSS
# ------------------------------------------------------------

total_target = filtered_production[
    "Target_Production"
].sum()

total_actual = filtered_production[
    "Actual_Production"
].sum()

missed_production = max(
    total_target - total_actual,
    0
)

production_loss_value = (
    missed_production
    * value_per_missed_unit
)


# ------------------------------------------------------------
# DOWNTIME COST
# ------------------------------------------------------------

total_downtime_hours = filtered_downtime[
    "Downtime_Hours"
].sum()

downtime_cost = (
    total_downtime_hours
    * cost_per_downtime_hour
)


# ------------------------------------------------------------
# QUALITY COST
# ------------------------------------------------------------

total_defects = filtered_quality[
    "Defective_Units"
].sum()

defect_cost = (
    total_defects
    * cost_per_defective_unit
)


# ------------------------------------------------------------
# TOTAL ESTIMATED IMPACT
# ------------------------------------------------------------

total_business_impact = (
    production_loss_value
    + downtime_cost
    + defect_cost
)


# ------------------------------------------------------------
# DISPLAY KPI CARDS
# ------------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Production Loss",
        f"₹{production_loss_value:,.0f}"
    )

with col2:

    st.metric(
        "Downtime Cost",
        f"₹{downtime_cost:,.0f}"
    )

with col3:

    st.metric(
        "Defect Cost",
        f"₹{defect_cost:,.0f}"
    )

with col4:

    st.metric(
        "Total Estimated Impact",
        f"₹{total_business_impact:,.0f}"
    )


# ------------------------------------------------------------
# IMPROVEMENT OPPORTUNITY
# ------------------------------------------------------------

potential_savings = (
    total_business_impact * 0.10
)

st.success(
    f"💡 **10% Loss Reduction Opportunity:** "
    f"If the identified losses are reduced by just 10%, "
    f"the estimated potential savings would be "
    f"**₹{potential_savings:,.0f}** for the selected period."
)


# ------------------------------------------------------------
# ASSUMPTIONS
# ------------------------------------------------------------

with st.expander("View Financial Assumptions"):

    st.write(
        f"• Downtime cost: ₹{cost_per_downtime_hour:,} per hour"
    )

    st.write(
        f"• Defective unit cost: "
        f"₹{cost_per_defective_unit:,} per unit"
    )

    st.write(
        f"• Missed production value: "
        f"₹{value_per_missed_unit:,} per unit"
    )

    st.caption(
        "These are illustrative assumptions for the "
        "portfolio project and should be replaced with "
        "company-specific financial data in a real deployment."
    )
# ============================================================
# PLANT PERFORMANCE BENCHMARKING
# ============================================================

st.markdown("---")

st.header("🏭 Plant Performance Benchmarking")


# ------------------------------------------------------------
# PRODUCTION PERFORMANCE BY PLANT
# ------------------------------------------------------------

plant_benchmark_production = (
    filtered_production
    .groupby("Plant")
    .agg(
        Target_Production=("Target_Production", "sum"),
        Actual_Production=("Actual_Production", "sum")
    )
)

plant_benchmark_production["Production_Achievement_%"] = (
    plant_benchmark_production["Actual_Production"]
    / plant_benchmark_production["Target_Production"]
    * 100
)


# ------------------------------------------------------------
# DOWNTIME BY PLANT
# ------------------------------------------------------------

plant_benchmark_downtime = (
    filtered_downtime
    .groupby("Plant")["Downtime_Hours"]
    .sum()
    .rename("Downtime_Hours")
)


# ------------------------------------------------------------
# QUALITY BY PLANT
# ------------------------------------------------------------

plant_benchmark_quality = (
    filtered_quality
    .groupby("Plant")
    .agg(
        Units_Produced=("Units_Produced", "sum"),
        Defective_Units=("Defective_Units", "sum")
    )
)

plant_benchmark_quality["Defect_Rate_%"] = (
    plant_benchmark_quality["Defective_Units"]
    / plant_benchmark_quality["Units_Produced"]
    * 100
)


# ------------------------------------------------------------
# COMBINE ALL THREE AREAS
# ------------------------------------------------------------

plant_benchmark = (
    plant_benchmark_production[
        ["Production_Achievement_%"]
    ]
    .join(
        plant_benchmark_downtime,
        how="outer"
    )
    .join(
        plant_benchmark_quality[
            ["Defect_Rate_%"]
        ],
        how="outer"
    )
)

plant_benchmark = plant_benchmark.dropna()


# ------------------------------------------------------------
# DISPLAY TABLE
# ------------------------------------------------------------

st.dataframe(
    plant_benchmark.style.format({
        "Production_Achievement_%": "{:.2f}%",
        "Downtime_Hours": "{:,.1f}",
        "Defect_Rate_%": "{:.2f}%"
    }),
    use_container_width=True
)


# ------------------------------------------------------------
# IDENTIFY BEST / WORST PLANTS
# ------------------------------------------------------------

if len(plant_benchmark) > 0:

    # Normalize each metric so higher = better
    production_score = (
        plant_benchmark["Production_Achievement_%"]
        / plant_benchmark["Production_Achievement_%"].max()
    )

    downtime_score = (
        1
        - (
            plant_benchmark["Downtime_Hours"]
            / plant_benchmark["Downtime_Hours"].max()
        )
    )

    quality_score = (
        1
        - (
            plant_benchmark["Defect_Rate_%"]
            / plant_benchmark["Defect_Rate_%"].max()
        )
    )

    # Overall performance score
    plant_benchmark["Overall_Score"] = (
        production_score * 0.40
        + downtime_score * 0.30
        + quality_score * 0.30
    ) * 100

    plant_benchmark = plant_benchmark.sort_values(
        "Overall_Score",
        ascending=False
    )

    best_plant = plant_benchmark.index[0]

    best_score = plant_benchmark.iloc[0]["Overall_Score"]

    worst_plant_benchmark = plant_benchmark.index[-1]

    worst_score = plant_benchmark.iloc[-1]["Overall_Score"]


    # --------------------------------------------------------
    # DISPLAY RESULTS
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.success(
            f"🏆 **Best Overall Plant: {best_plant}**\n\n"
            f"Overall performance score: "
            f"**{best_score:.1f}/100**"
        )

    with col2:

        st.warning(
            f"⚠️ **Priority Plant: "
            f"{worst_plant_benchmark}**\n\n"
            f"Overall performance score: "
            f"**{worst_score:.1f}/100**"
        )


    # --------------------------------------------------------
    # SCORE CHART
    # --------------------------------------------------------

    st.subheader("Overall Plant Performance Score")

    st.bar_chart(
        plant_benchmark["Overall_Score"]
    )


    st.caption(
        "Overall score weighting: 40% production achievement, "
        "30% downtime performance and 30% quality performance."
    )

else:

    st.info(
        "Not enough plant-level data is available for "
        "benchmarking."
    )
    # ============================================================
# ASK PLANTPULSE
# ============================================================

st.markdown("---")

st.header("❓ Ask PlantPulse")

st.caption(
    "Select a business question to instantly analyze "
    "the currently filtered operational data."
)


question = st.selectbox(
    "What would you like to know?",
    [
        "Which plant has the highest downtime?",
        "Which plant has the lowest production achievement?",
        "Which machine has the highest defect rate?",
        "What is the biggest source of downtime?",
        "How much downtime is recorded?",
        "How many defective units were recorded?",
        "What is the overall production achievement?"
    ]
)


# ------------------------------------------------------------
# QUESTION 1 — HIGHEST DOWNTIME PLANT
# ------------------------------------------------------------

if question == "Which plant has the highest downtime?":

    if len(plant_benchmark) > 0:

        highest_downtime_plant = (
            plant_benchmark["Downtime_Hours"].idxmax()
        )

        highest_downtime_value = (
            plant_benchmark.loc[
                highest_downtime_plant,
                "Downtime_Hours"
            ]
        )

        st.error(
            f"🔴 **{highest_downtime_plant}** has the highest "
            f"downtime at **{highest_downtime_value:,.1f} hours**."
        )

    else:

        st.info("Not enough data available.")


# ------------------------------------------------------------
# QUESTION 2 — LOWEST PRODUCTION ACHIEVEMENT
# ------------------------------------------------------------

elif question == "Which plant has the lowest production achievement?":

    if len(plant_benchmark) > 0:

        lowest_production_plant = (
            plant_benchmark[
                "Production_Achievement_%"
            ].idxmin()
        )

        lowest_production_value = (
            plant_benchmark.loc[
                lowest_production_plant,
                "Production_Achievement_%"
            ]
        )

        st.warning(
            f"⚠️ **{lowest_production_plant}** has the lowest "
            f"production achievement at "
            f"**{lowest_production_value:.2f}%**."
        )

    else:

        st.info("Not enough data available.")


# ------------------------------------------------------------
# QUESTION 3 — HIGHEST DEFECT MACHINE
# ------------------------------------------------------------

elif question == "Which machine has the highest defect rate?":

    if len(machine_quality) > 0:

        highest_defect_machine = (
            machine_quality[
                "Defect_Rate"
            ].idxmax()
        )

        highest_defect_value = (
            machine_quality.loc[
                highest_defect_machine,
                "Defect_Rate"
            ]
        )

        st.error(
            f"🔴 **{highest_defect_machine}** has the highest "
            f"defect rate at **{highest_defect_value:.2f}%**."
        )

    else:

        st.info("Not enough data available.")


# ------------------------------------------------------------
# QUESTION 4 — BIGGEST DOWNTIME SOURCE
# ------------------------------------------------------------

elif question == "What is the biggest source of downtime?":

    if len(downtime_analysis) > 0:

        biggest_downtime_source = (
            downtime_analysis.index[0]
        )

        biggest_downtime_share = (
            downtime_analysis.iloc[0]["Share_of_Total_%"]
        )

        biggest_downtime_hours = (
            downtime_analysis.iloc[0]["Downtime_Hours"]
        )

        st.warning(
            f"⚠️ **{biggest_downtime_source}** is the biggest "
            f"downtime source, accounting for "
            f"**{biggest_downtime_hours:,.1f} hours** "
            f"(**{biggest_downtime_share:.2f}%** of total downtime)."
        )

    else:

        st.info("No downtime data available.")


# ------------------------------------------------------------
# QUESTION 5 — TOTAL DOWNTIME
# ------------------------------------------------------------

elif question == "How much downtime is recorded?":

    total_downtime_question = (
        filtered_downtime["Downtime_Hours"].sum()
    )

    st.info(
        f"📉 Total recorded downtime for the current "
        f"selection is **{total_downtime_question:,.1f} hours**."
    )


# ------------------------------------------------------------
# QUESTION 6 — TOTAL DEFECTS
# ------------------------------------------------------------

elif question == "How many defective units were recorded?":

    total_defects_question = (
        filtered_quality["Defective_Units"].sum()
    )

    st.info(
        f"🔧 The current selection contains "
        f"**{total_defects_question:,.0f} defective units**."
    )


# ------------------------------------------------------------
# QUESTION 7 — OVERALL PRODUCTION
# ------------------------------------------------------------

elif question == "What is the overall production achievement?":

    question_target = (
        filtered_production["Target_Production"].sum()
    )

    question_actual = (
        filtered_production["Actual_Production"].sum()
    )

    if question_target > 0:

        question_achievement = (
            question_actual
            / question_target
            * 100
        )

        st.info(
            f"📊 Overall production achievement is "
            f"**{question_achievement:.2f}%** of target."
        )

    else:

        st.info("Production target data is unavailable.")

# ============================================================
# SQL ANALYTICS — LIVE DATABASE QUERY
# ============================================================

st.markdown("---")

st.header("🗄️ SQL Analytics")

# Convert selected dates to strings for SQLite
sql_start_date = str(start_date)
sql_end_date = str(end_date)


# ============================================================
# BUILD SQL QUERY DYNAMICALLY
# ============================================================

sql_conditions = [
    "Date BETWEEN ? AND ?"
]

sql_params = [
    sql_start_date,
    sql_end_date
]


# ------------------------------------------------------------
# PLANT FILTER
# ------------------------------------------------------------

if selected_plant != "All":

    sql_conditions.append("Plant = ?")
    sql_params.append(selected_plant)


# ------------------------------------------------------------
# MACHINE FILTER
# ------------------------------------------------------------

if selected_machine != "All":

    sql_conditions.append("Machine = ?")
    sql_params.append(selected_machine)


# ------------------------------------------------------------
# FINAL SQL QUERY
# ------------------------------------------------------------

sql_test_query = f"""
SELECT
    Plant,
    Machine,

    SUM(Target_Production) AS Target_Production,

    SUM(Actual_Production) AS Actual_Production,

    ROUND(
        SUM(Actual_Production) * 100.0
        / NULLIF(SUM(Target_Production), 0),
        2
    ) AS Production_Achievement

FROM production

WHERE {" AND ".join(sql_conditions)}

GROUP BY Plant, Machine

ORDER BY Production_Achievement DESC;
"""


# ============================================================
# RUN SQL QUERY
# ============================================================

sql_plant_result = pd.read_sql_query(
    sql_test_query,
    sql_connection,
    params=sql_params
)


# ============================================================
# DISPLAY RESULT
# ============================================================

st.subheader("Production Performance — SQL")

st.dataframe(
    sql_plant_result,
    use_container_width=True
)
# ============================================================
# SQL QUALITY ANALYSIS
# ============================================================

st.markdown("---")

st.subheader("🔎 Machine Defect Analysis")


quality_conditions = [
    "Date BETWEEN ? AND ?"
]

quality_params = [
    sql_start_date,
    sql_end_date
]


# ------------------------------------------------------------
# PLANT FILTER
# ------------------------------------------------------------

if selected_plant != "All":

    quality_conditions.append("Plant = ?")
    quality_params.append(selected_plant)


# ------------------------------------------------------------
# MACHINE FILTER
# ------------------------------------------------------------

if selected_machine != "All":

    quality_conditions.append("Machine = ?")
    quality_params.append(selected_machine)


# ------------------------------------------------------------
# QUALITY SQL QUERY
# ------------------------------------------------------------

quality_query = f"""
SELECT

    Plant,

    Machine,

    SUM(Units_Produced) AS Units_Produced,

    SUM(Defective_Units) AS Defective_Units,

    ROUND(
        SUM(Defective_Units) * 100.0
        / NULLIF(SUM(Units_Produced), 0),
        2
    ) AS Defect_Rate_Percent

FROM quality

WHERE {" AND ".join(quality_conditions)}

GROUP BY Plant, Machine

ORDER BY Defect_Rate_Percent DESC;
"""


# ------------------------------------------------------------
# RUN QUERY
# ------------------------------------------------------------

quality_sql_result = pd.read_sql_query(
    quality_query,
    sql_connection,
    params=quality_params
)


# ------------------------------------------------------------
# DISPLAY RESULT
# ------------------------------------------------------------

st.dataframe(
    quality_sql_result,
    use_container_width=True
)
# ============================================================
# SQL DOWNTIME ANALYSIS
# ============================================================

st.markdown("---")

st.subheader("⏱️ Downtime Analysis")


downtime_conditions = [
    "Date BETWEEN ? AND ?"
]

downtime_params = [
    sql_start_date,
    sql_end_date
]


# ------------------------------------------------------------
# PLANT FILTER
# ------------------------------------------------------------

if selected_plant != "All":

    downtime_conditions.append("Plant = ?")
    downtime_params.append(selected_plant)


# ------------------------------------------------------------
# MACHINE FILTER
# ------------------------------------------------------------

if selected_machine != "All":

    downtime_conditions.append("Machine = ?")
    downtime_params.append(selected_machine)


# ------------------------------------------------------------
# DOWNTIME SQL QUERY
# ------------------------------------------------------------

downtime_query = f"""
SELECT

    Plant,

    Machine,

    Downtime_Reason,

    ROUND(
        SUM(Downtime_Hours),
        2
    ) AS Total_Downtime_Hours

FROM downtime

WHERE {" AND ".join(downtime_conditions)}

GROUP BY
    Plant,
    Machine,
    Downtime_Reason

ORDER BY
    Total_Downtime_Hours DESC;
"""


# ------------------------------------------------------------
# RUN QUERY
# ------------------------------------------------------------

downtime_sql_result = pd.read_sql_query(
    downtime_query,
    sql_connection,
    params=downtime_params
)


# ------------------------------------------------------------
# DISPLAY RESULT
# ------------------------------------------------------------

st.dataframe(
    downtime_sql_result,
    use_container_width=True
)
# ============================================================
# SQL OPERATIONAL RISK SCORE
# ============================================================

st.markdown("---")

#st.subheader("🚨 Operational Risk Analysis")


# ============================================================
# PRODUCTION FILTERS
# ============================================================

production_conditions = [
    "Date BETWEEN ? AND ?"
]

production_params = [
    sql_start_date,
    sql_end_date
]


if selected_plant != "All":

    production_conditions.append("Plant = ?")
    production_params.append(selected_plant)


if selected_machine != "All":

    production_conditions.append("Machine = ?")
    production_params.append(selected_machine)


# ============================================================
# QUALITY FILTERS
# ============================================================

quality_conditions = [
    "Date BETWEEN ? AND ?"
]

quality_params = [
    sql_start_date,
    sql_end_date
]


if selected_plant != "All":

    quality_conditions.append("Plant = ?")
    quality_params.append(selected_plant)


if selected_machine != "All":

    quality_conditions.append("Machine = ?")
    quality_params.append(selected_machine)


# ============================================================
# DOWNTIME FILTERS
# ============================================================

downtime_conditions = [
    "Date BETWEEN ? AND ?"
]

downtime_params = [
    sql_start_date,
    sql_end_date
]


if selected_plant != "All":

    downtime_conditions.append("Plant = ?")
    downtime_params.append(selected_plant)


if selected_machine != "All":

    downtime_conditions.append("Machine = ?")
    downtime_params.append(selected_machine)


# ============================================================
# OPERATIONAL RISK SQL QUERY
# ============================================================
st.header("⚠️ Risk & Prioritization")
st.caption(
    "Operational Risk Score combines production shortfall, downtime, "
    "and defect rate. Higher scores indicate greater operational risk."
)
st.markdown("---")
risk_query = f"""

WITH production_summary AS (

    SELECT

        Plant,

        Machine,

        SUM(Target_Production) AS Target_Production,

        SUM(Actual_Production) AS Actual_Production

    FROM production

    WHERE {" AND ".join(production_conditions)}

    GROUP BY Plant, Machine
),


quality_summary AS (

    SELECT

        Plant,

        Machine,

        SUM(Units_Produced) AS Units_Produced,

        SUM(Defective_Units) AS Defective_Units

    FROM quality

    WHERE {" AND ".join(quality_conditions)}

    GROUP BY Plant, Machine
),


downtime_summary AS (

    SELECT

        Plant,

        Machine,

        SUM(Downtime_Hours) AS Downtime_Hours

    FROM downtime

    WHERE {" AND ".join(downtime_conditions)}

    GROUP BY Plant, Machine
)


SELECT

    p.Plant,

    p.Machine,


    ROUND(

        p.Actual_Production * 100.0

        / NULLIF(p.Target_Production, 0),

        2

    ) AS Production_Achievement,


    ROUND(

        q.Defective_Units * 100.0

        / NULLIF(q.Units_Produced, 0),

        2

    ) AS Defect_Rate,


    ROUND(

        COALESCE(d.Downtime_Hours, 0),

        2

    ) AS Downtime_Hours,


    ROUND(

        (

            100 -

            (

                p.Actual_Production * 100.0

                / NULLIF(p.Target_Production, 0)

            )

        )

        +

        (

            COALESCE(d.Downtime_Hours, 0)

            / 100.0

        )

        +

        (

            COALESCE(

                q.Defective_Units * 100.0

                / NULLIF(q.Units_Produced, 0),

                0

            ) * 5

        ),

        2

    ) AS Operational_Risk_Score


FROM production_summary p


LEFT JOIN quality_summary q

    ON p.Plant = q.Plant

    AND p.Machine = q.Machine


LEFT JOIN downtime_summary d

    ON p.Plant = d.Plant

    AND p.Machine = d.Machine


ORDER BY Operational_Risk_Score DESC;

"""


# ============================================================
# RUN RISK QUERY
# ============================================================

risk_sql_result = pd.read_sql_query(

    risk_query,

    sql_connection,

    params=(
        production_params
        + quality_params
        + downtime_params
    )

)
# ============================================================
# RISK LEVEL CLASSIFICATION
# ============================================================

# ============================================================
# GLOBAL RISK THRESHOLDS
# ============================================================
# Calculate risk thresholds using ALL plants and ALL machines
# for the currently selected date range.
# These thresholds remain constant when Plant/Machine filters
# are changed.

benchmark_query = """
WITH production_summary AS (

    SELECT
        Plant,
        Machine,

        SUM(Target_Production) AS Target_Production,

        SUM(Actual_Production) AS Actual_Production

    FROM production

    WHERE Date BETWEEN ? AND ?

    GROUP BY Plant, Machine
),

quality_summary AS (

    SELECT
        Plant,
        Machine,

        SUM(Units_Produced) AS Units_Produced,

        SUM(Defective_Units) AS Defective_Units

    FROM quality

    WHERE Date BETWEEN ? AND ?

    GROUP BY Plant, Machine
),

downtime_summary AS (

    SELECT
        Plant,
        Machine,

        SUM(Downtime_Hours) AS Downtime_Hours

    FROM downtime

    WHERE Date BETWEEN ? AND ?

    GROUP BY Plant, Machine
)

SELECT

    p.Plant,

    p.Machine,

    ROUND(

        (
            100 -

            (
                p.Actual_Production * 100.0
                / NULLIF(p.Target_Production, 0)
            )
        )

        +

        (
            COALESCE(d.Downtime_Hours, 0)
            / 100.0
        )

        +

        (
            COALESCE(
                q.Defective_Units * 100.0
                / NULLIF(q.Units_Produced, 0),
                0
            ) * 5
        ),

        2

    ) AS Operational_Risk_Score

FROM production_summary p

LEFT JOIN quality_summary q

    ON p.Plant = q.Plant
    AND p.Machine = q.Machine

LEFT JOIN downtime_summary d

    ON p.Plant = d.Plant
    AND p.Machine = d.Machine
"""


benchmark_result = pd.read_sql_query(
    benchmark_query,
    sql_connection,
    params=(
        sql_start_date,
        sql_end_date,
        sql_start_date,
        sql_end_date,
        sql_start_date,
        sql_end_date
    )
)


# ============================================================
# CALCULATE GLOBAL THRESHOLDS
# ============================================================

if not benchmark_result.empty:

    low_threshold = benchmark_result[
        "Operational_Risk_Score"
    ].quantile(0.50)

    high_threshold = benchmark_result[
        "Operational_Risk_Score"
    ].quantile(0.80)


    # --------------------------------------------------------
    # APPLY GLOBAL THRESHOLDS TO FILTERED RESULTS
    # --------------------------------------------------------

    def classify_risk(score):

        if score >= high_threshold:
            return "High Risk"

        elif score >= low_threshold:
            return "Medium Risk"

        else:
            return "Low Risk"


    risk_sql_result["Risk_Level"] = (
        risk_sql_result["Operational_Risk_Score"]
        .apply(classify_risk)
    )

# ============================================================
# RISK DISTRIBUTION
# ============================================================

st.subheader("📊 Risk Distribution")


risk_counts = (
    risk_sql_result["Risk_Level"]
    .value_counts()
    .reindex(
        ["High Risk", "Medium Risk", "Low Risk"],
        fill_value=0
    )
)


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "🔴 High Risk",
        int(risk_counts["High Risk"])
    )


with col2:

    st.metric(
        "🟡 Medium Risk",
        int(risk_counts["Medium Risk"])
    )


with col3:

    st.metric(
        "🟢 Low Risk",
        int(risk_counts["Low Risk"])
    )
# ============================================================
# HIGHEST RISK KPI
# ============================================================

if not risk_sql_result.empty:

    highest_risk_machine = risk_sql_result.iloc[0]["Machine"]

    highest_risk_score = risk_sql_result.iloc[0][
        "Operational_Risk_Score"
    ]

    highest_risk_plant = risk_sql_result.iloc[0]["Plant"]


    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            "🚨 Highest-Risk Machine",
            highest_risk_machine
        )


    with col2:

        st.metric(
            "Operational Risk Score",
            highest_risk_score
        )


    st.caption(
        f"Highest-risk combination: "
        f"{highest_risk_plant} — {highest_risk_machine}"
    )

# ============================================================
# DISPLAY RESULT
# ============================================================

st.dataframe(

    risk_sql_result,

    use_container_width=True

)
# ============================================================
# PRIORITY MACHINES
# ============================================================
# ============================================================
# PRIORITY MACHINES
# ============================================================

st.markdown("---")

st.subheader("🎯 Priority Machines for Investigation")


if not risk_sql_result.empty:

    # ========================================================
    # CURRENT FILTERED RESULT
    # ========================================================

    priority_result = risk_sql_result.copy()


    # ========================================================
    # PRODUCTION SHORTFALL
    # ========================================================

    priority_result["Production_Shortfall"] = (
        100 - priority_result["Production_Achievement"]
    ).round(2)


    # ========================================================
    # GLOBAL BENCHMARK QUERY
    #
    # IMPORTANT:
    # This query intentionally ignores Plant and Machine
    # filters. It uses the complete dataset for the selected
    # date range.
    # ========================================================

    action_benchmark_query = """

    WITH production_summary AS (

        SELECT

            Plant,

            Machine,

            SUM(Target_Production) AS Target_Production,

            SUM(Actual_Production) AS Actual_Production

        FROM production

        WHERE Date BETWEEN ? AND ?

        GROUP BY Plant, Machine
    ),


    quality_summary AS (

        SELECT

            Plant,

            Machine,

            SUM(Units_Produced) AS Units_Produced,

            SUM(Defective_Units) AS Defective_Units

        FROM quality

        WHERE Date BETWEEN ? AND ?

        GROUP BY Plant, Machine
    ),


    downtime_summary AS (

        SELECT

            Plant,

            Machine,

            SUM(Downtime_Hours) AS Downtime_Hours

        FROM downtime

        WHERE Date BETWEEN ? AND ?

        GROUP BY Plant, Machine
    )


    SELECT

        p.Plant,

        p.Machine,


        ROUND(

            p.Actual_Production * 100.0
            / NULLIF(p.Target_Production, 0),

            2

        ) AS Production_Achievement,


        ROUND(

            q.Defective_Units * 100.0
            / NULLIF(q.Units_Produced, 0),

            2

        ) AS Defect_Rate,


        ROUND(

            COALESCE(d.Downtime_Hours, 0),

            2

        ) AS Downtime_Hours


    FROM production_summary p


    LEFT JOIN quality_summary q

        ON p.Plant = q.Plant

        AND p.Machine = q.Machine


    LEFT JOIN downtime_summary d

        ON p.Plant = d.Plant

        AND p.Machine = d.Machine

    """


    action_benchmark_result = pd.read_sql_query(

        action_benchmark_query,

        sql_connection,

        params=(

            sql_start_date,

            sql_end_date,

            sql_start_date,

            sql_end_date,

            sql_start_date,

            sql_end_date

        )

    )


    # ========================================================
    # CALCULATE GLOBAL BENCHMARKS
    # ========================================================

    if not action_benchmark_result.empty:

        # Production: HIGHER SHORTFALL = WORSE

        action_benchmark_result["Production_Shortfall"] = (

            100
            - action_benchmark_result["Production_Achievement"]

        )


        production_threshold = (
            action_benchmark_result[
                "Production_Shortfall"
            ]
            .quantile(0.80)
        )


        # Quality: HIGHER DEFECT RATE = WORSE

        quality_threshold = (
            action_benchmark_result[
                "Defect_Rate"
            ]
            .quantile(0.80)
        )


        # Downtime: HIGHER HOURS = WORSE

        downtime_threshold = (
            action_benchmark_result[
                "Downtime_Hours"
            ]
            .quantile(0.80)
        )


        # ====================================================
        # PRIMARY ACTION FUNCTION
        # ====================================================

        def identify_action(row):

            production_gap = row["Production_Shortfall"]

            defect_rate = row["Defect_Rate"]

            downtime = row["Downtime_Hours"]


            # -----------------------------------------------
            # Calculate severity relative to GLOBAL benchmark
            # -----------------------------------------------

            production_severity = (

                production_gap / production_threshold

                if production_threshold > 0

                else 0

            )


            quality_severity = (

                defect_rate / quality_threshold

                if quality_threshold > 0

                else 0

            )


            downtime_severity = (

                downtime / downtime_threshold

                if downtime_threshold > 0

                else 0

            )


            # -----------------------------------------------
            # Find the dominant problem
            # -----------------------------------------------

            severity_scores = {

                "Investigate production":
                    production_severity,

                "Investigate quality":
                    quality_severity,

                "Investigate downtime":
                    downtime_severity

            }


            highest_action = max(

                severity_scores,

                key=severity_scores.get

            )


            highest_severity = severity_scores[
                highest_action
            ]


            # -----------------------------------------------
            # If none exceeds its benchmark,
            # machine does not have a dominant issue
            # -----------------------------------------------

            if highest_severity < 1:

                return "Monitor"


            return highest_action


        # ====================================================
        # APPLY ACTION TO FILTERED RESULT
        # ====================================================

        priority_result["Primary_Action"] = (

            priority_result.apply(

                identify_action,

                axis=1

            )

        )


    else:

        priority_result["Primary_Action"] = "Monitor"


    # ========================================================
    # SORT BY OPERATIONAL RISK
    # ========================================================

    priority_result = priority_result.sort_values(

        "Operational_Risk_Score",

        ascending=False

    )


    # ========================================================
    # SELECT FINAL COLUMNS
    # ========================================================

    priority_result = priority_result[

        [

            "Plant",

            "Machine",

            "Risk_Level",

            "Operational_Risk_Score",

            "Production_Shortfall",

            "Defect_Rate",

            "Downtime_Hours",

            "Primary_Action"

        ]

    ]


    # ========================================================
    # DISPLAY
    # ========================================================

    st.dataframe(

        priority_result,

        use_container_width=True

    )
else:

    st.info(

        "No machines match the selected filters."

    )

    # ============================================================
# TOP PRIORITY MACHINE
# ============================================================

if not priority_result.empty:

    top_priority = priority_result.iloc[0]

    st.markdown("---")

    st.subheader("🚨 Top Priority Machine")

    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Plant",
            top_priority["Plant"]
        )


    with col2:

        st.metric(
            "Machine",
            top_priority["Machine"]
        )


    with col3:

        st.metric(
            "Primary Action",
            top_priority["Primary_Action"]
        )


    st.caption(
        f"Risk Score: "
        f"{top_priority['Operational_Risk_Score']:.2f}"
    )
    # ============================================================
# OPERATIONAL RISK TREND
# ============================================================

st.markdown("---")

st.subheader("📈 Operational Risk Trend")


risk_trend_query = """

WITH production_daily AS (

    SELECT
        Date,
        Plant,
        Machine,
        SUM(Target_Production) AS Target_Production,
        SUM(Actual_Production) AS Actual_Production

    FROM production

    WHERE Date BETWEEN ? AND ?

    GROUP BY Date, Plant, Machine
),


quality_daily AS (

    SELECT
        Date,
        Plant,
        Machine,
        SUM(Units_Produced) AS Units_Produced,
        SUM(Defective_Units) AS Defective_Units

    FROM quality

    WHERE Date BETWEEN ? AND ?

    GROUP BY Date, Plant, Machine
),


downtime_daily AS (

    SELECT
        Date,
        Plant,
        Machine,
        SUM(Downtime_Hours) AS Downtime_Hours

    FROM downtime

    WHERE Date BETWEEN ? AND ?

    GROUP BY Date, Plant, Machine
)


SELECT

    p.Date,

    p.Plant,

    p.Machine,

    ROUND(

        (
            100 -

            (
                p.Actual_Production * 100.0
                / NULLIF(p.Target_Production, 0)
            )
        )

        +

        (
            COALESCE(d.Downtime_Hours, 0)
            / 100.0
        )

        +

        (
            COALESCE(
                q.Defective_Units * 100.0
                / NULLIF(q.Units_Produced, 0),
                0
            ) * 5
        ),

        2

    ) AS Operational_Risk_Score


FROM production_daily p


LEFT JOIN quality_daily q

    ON p.Date = q.Date

    AND p.Plant = q.Plant

    AND p.Machine = q.Machine


LEFT JOIN downtime_daily d

    ON p.Date = d.Date

    AND p.Plant = d.Plant

    AND p.Machine = d.Machine

"""


risk_trend_result = pd.read_sql_query(

    risk_trend_query,

    sql_connection,

    params=(

        sql_start_date,
        sql_end_date,

        sql_start_date,
        sql_end_date,

        sql_start_date,
        sql_end_date

    )

)


# ============================================================
# APPLY CURRENT FILTERS
# ============================================================

if selected_plant != "All":

    risk_trend_result = risk_trend_result[
        risk_trend_result["Plant"] == selected_plant
    ]


if selected_machine != "All":

    risk_trend_result = risk_trend_result[
        risk_trend_result["Machine"] == selected_machine
    ]


# ============================================================
# DAILY AVERAGE RISK
# ============================================================

if not risk_trend_result.empty:

    risk_trend_result["Date"] = pd.to_datetime(
        risk_trend_result["Date"]
    )


    risk_trend_daily = (

        risk_trend_result

        .groupby("Date", as_index=False)

        ["Operational_Risk_Score"]

        .mean()

    )


    risk_trend_daily["Operational_Risk_Score"] = (

        risk_trend_daily["Operational_Risk_Score"]

        .round(2)

    )


    st.line_chart(

        risk_trend_daily.set_index("Date")

    )


else:

    st.info(
        "No risk trend data available for the selected filters."
    )
# ============================================================
# MACHINE RISK COMPARISON
# ============================================================

st.markdown("---")

st.subheader("📊 Machine Risk Comparison")


if not risk_sql_result.empty:

    machine_comparison = risk_sql_result[
        [
            "Plant",
            "Machine",
            "Risk_Level",
            "Operational_Risk_Score"
        ]
    ].copy()


    # --------------------------------------------------------
    # MACHINE LABEL
    # --------------------------------------------------------

    machine_comparison["Machine_Label"] = (
        machine_comparison["Plant"]
        + " - "
        + machine_comparison["Machine"]
    )


    # --------------------------------------------------------
    # SORT HIGHEST RISK FIRST
    # --------------------------------------------------------

    machine_comparison = machine_comparison.sort_values(
        "Operational_Risk_Score",
        ascending=False
    )


    # --------------------------------------------------------
    # BAR CHART
    # --------------------------------------------------------

    machine_comparison_chart = (
        machine_comparison[
            [
                "Machine_Label",
                "Operational_Risk_Score"
            ]
        ]
        .set_index("Machine_Label")
    )


    st.bar_chart(
        machine_comparison_chart
    )


    # --------------------------------------------------------
    # RISK SUMMARY TABLE
    # --------------------------------------------------------

    st.markdown("#### Risk Summary")


    risk_summary = machine_comparison[
        [
            "Plant",
            "Machine",
            "Risk_Level",
            "Operational_Risk_Score"
        ]
    ].copy()


    risk_summary["Operational_Risk_Score"] = (
        risk_summary["Operational_Risk_Score"]
        .round(2)
    )


    st.dataframe(
        risk_summary,
        use_container_width=True,
        hide_index=True
    )


else:

    st.info(
        "No machine risk data available for the selected filters."
    )
# ============================================================
# PRODUCTION PERFORMANCE ANALYSIS
# ============================================================

st.markdown("---")

st.header("🏭 Production Performance")


# ============================================================
# LOAD PRODUCTION DATA DIRECTLY FROM DATABASE
# ============================================================

production_performance = pd.read_sql_query(
    """
    SELECT
        Date,
        Plant,
        Machine,
        Target_Production,
        Actual_Production
    FROM production
    """,
    sql_connection
)


# Convert Date to datetime
production_performance["Date"] = pd.to_datetime(
    production_performance["Date"]
)


# ============================================================
# DATE FILTER
# ============================================================

if isinstance(selected_dates, tuple) and len(selected_dates) == 2:

    start_date = pd.to_datetime(
        selected_dates[0]
    )

    end_date = pd.to_datetime(
        selected_dates[1]
    )

    production_performance = production_performance[
        (
            production_performance["Date"] >= start_date
        )
        &
        (
            production_performance["Date"] <= end_date
        )
    ]


# ============================================================
# PLANT FILTER
# ============================================================

if selected_plant != "All":

    production_performance = production_performance[
        production_performance["Plant"] == selected_plant
    ]


# ============================================================
# MACHINE FILTER
# ============================================================

if selected_machine != "All":

    production_performance = production_performance[
        production_performance["Machine"] == selected_machine
    ]


# ============================================================
# PRODUCTION ANALYSIS
# ============================================================

if not production_performance.empty:

    production_summary = (

        production_performance

        .groupby(
            ["Plant", "Machine"],
            as_index=False
        )

        .agg(
            Target_Production=(
                "Target_Production",
                "sum"
            ),

            Actual_Production=(
                "Actual_Production",
                "sum"
            )
        )
    )


    # ========================================================
    # PRODUCTION ACHIEVEMENT
    # ========================================================

    production_summary["Production_Achievement"] = (

        production_summary["Actual_Production"]

        * 100.0

        /

        production_summary[
            "Target_Production"
        ].replace(0, pd.NA)

    ).round(2)


    # ========================================================
    # PRODUCTION SHORTFALL
    # ========================================================

    production_summary["Production_Shortfall"] = (

        100

        - production_summary[
            "Production_Achievement"
        ]

    ).round(2)


    # ========================================================
    # MACHINE LABEL
    # ========================================================

    production_summary["Machine_Label"] = (

        production_summary["Plant"].astype(str)

        + " - "

        + production_summary["Machine"].astype(str)

    )


    # ========================================================
    # TARGET VS ACTUAL CHART
    # ========================================================

    production_chart = (

        production_summary[
            [
                "Machine_Label",
                "Target_Production",
                "Actual_Production"
            ]
        ]

        .set_index("Machine_Label")

    )


    st.bar_chart(
        production_chart
    )


    # ========================================================
    # PRODUCTION SUMMARY TABLE
    # ========================================================

    st.markdown("#### Production Summary")


    production_display = production_summary[
        [
            "Plant",
            "Machine",
            "Target_Production",
            "Actual_Production",
            "Production_Achievement",
            "Production_Shortfall"
        ]
    ].copy()


    production_display[
        "Target_Production"
    ] = production_display[
        "Target_Production"
    ].round(2)


    production_display[
        "Actual_Production"
    ] = production_display[
        "Actual_Production"
    ].round(2)


    st.dataframe(
        production_display,
        use_container_width=True,
        hide_index=True
    )


else:

    st.info(
        "No production data available for the selected filters."
    )
    # ============================================================
# QUALITY PERFORMANCE ANALYSIS
# ============================================================

st.markdown("---")

st.header("🔍 Quality Performance")


# ============================================================
# LOAD QUALITY DATA DIRECTLY FROM DATABASE
# ============================================================

quality_performance = pd.read_sql_query(
    """
    SELECT
        Date,
        Plant,
        Machine,
        Units_Produced,
        Defective_Units
    FROM quality
    """,
    sql_connection
)


# Convert Date to datetime
quality_performance["Date"] = pd.to_datetime(
    quality_performance["Date"]
)


# ============================================================
# DATE FILTER
# ============================================================

if isinstance(selected_dates, tuple) and len(selected_dates) == 2:

    start_date = pd.to_datetime(
        selected_dates[0]
    )

    end_date = pd.to_datetime(
        selected_dates[1]
    )

    quality_performance = quality_performance[
        (
            quality_performance["Date"] >= start_date
        )
        &
        (
            quality_performance["Date"] <= end_date
        )
    ]


# ============================================================
# PLANT FILTER
# ============================================================

if selected_plant != "All":

    quality_performance = quality_performance[
        quality_performance["Plant"] == selected_plant
    ]


# ============================================================
# MACHINE FILTER
# ============================================================

if selected_machine != "All":

    quality_performance = quality_performance[
        quality_performance["Machine"] == selected_machine
    ]


# ============================================================
# QUALITY ANALYSIS
# ============================================================

if not quality_performance.empty:

    quality_summary = (

        quality_performance

        .groupby(
            ["Plant", "Machine"],
            as_index=False
        )

        .agg(
            Units_Produced=(
                "Units_Produced",
                "sum"
            ),

            Defective_Units=(
                "Defective_Units",
                "sum"
            )
        )
    )


    # ========================================================
    # DEFECT RATE
    # ========================================================

    quality_summary["Defect_Rate"] = (

        quality_summary["Defective_Units"]

        * 100.0

        /

        quality_summary[
            "Units_Produced"
        ].replace(0, pd.NA)

    ).round(2)


    # ========================================================
    # MACHINE LABEL
    # ========================================================

    quality_summary["Machine_Label"] = (

        quality_summary["Plant"].astype(str)

        + " - "

        + quality_summary["Machine"].astype(str)

    )


    # ========================================================
    # DEFECT RATE CHART
    # ========================================================

    quality_chart = (

        quality_summary[
            [
                "Machine_Label",
                "Defect_Rate"
            ]
        ]

        .set_index("Machine_Label")

    )


    st.bar_chart(
        quality_chart
    )


    # ========================================================
    # QUALITY SUMMARY TABLE
    # ========================================================

    st.markdown("#### Quality Summary")


    quality_display = quality_summary[
        [
            "Plant",
            "Machine",
            "Units_Produced",
            "Defective_Units",
            "Defect_Rate"
        ]
    ].copy()


    quality_display[
        "Units_Produced"
    ] = quality_display[
        "Units_Produced"
    ].round(2)


    quality_display[
        "Defective_Units"
    ] = quality_display[
        "Defective_Units"
    ].round(2)


    st.dataframe(
        quality_display,
        use_container_width=True,
        hide_index=True
    )


else:

    st.info(
        "No quality data available for the selected filters."
    )
    # ============================================================
# DOWNTIME PERFORMANCE ANALYSIS
# ============================================================

st.markdown("---")

st.header("⏱️ Downtime Analysis")


# ============================================================
# LOAD DOWNTIME DATA DIRECTLY FROM DATABASE
# ============================================================

downtime_performance = pd.read_sql_query(
    """
    SELECT
        Date,
        Plant,
        Machine,
        Downtime_Hours
    FROM downtime
    """,
    sql_connection
)


# Convert Date to datetime
downtime_performance["Date"] = pd.to_datetime(
    downtime_performance["Date"]
)


# ============================================================
# DATE FILTER
# ============================================================

if isinstance(selected_dates, tuple) and len(selected_dates) == 2:

    start_date = pd.to_datetime(
        selected_dates[0]
    )

    end_date = pd.to_datetime(
        selected_dates[1]
    )

    downtime_performance = downtime_performance[
        (
            downtime_performance["Date"] >= start_date
        )
        &
        (
            downtime_performance["Date"] <= end_date
        )
    ]


# ============================================================
# PLANT FILTER
# ============================================================

if selected_plant != "All":

    downtime_performance = downtime_performance[
        downtime_performance["Plant"] == selected_plant
    ]


# ============================================================
# MACHINE FILTER
# ============================================================

if selected_machine != "All":

    downtime_performance = downtime_performance[
        downtime_performance["Machine"] == selected_machine
    ]


# ============================================================
# DOWNTIME ANALYSIS
# ============================================================

if not downtime_performance.empty:

    downtime_summary = (

        downtime_performance

        .groupby(
            ["Plant", "Machine"],
            as_index=False
        )

        .agg(
            Downtime_Hours=(
                "Downtime_Hours",
                "sum"
            )
        )
    )


    # ========================================================
    # ROUND DOWNTIME
    # ========================================================

    downtime_summary["Downtime_Hours"] = (

        downtime_summary[
            "Downtime_Hours"
        ]

        .round(2)

    )


    # ========================================================
    # MACHINE LABEL
    # ========================================================

    downtime_summary["Machine_Label"] = (

        downtime_summary["Plant"].astype(str)

        + " - "

        + downtime_summary["Machine"].astype(str)

    )


    # ========================================================
    # SORT HIGHEST DOWNTIME FIRST
    # ========================================================

    downtime_summary = downtime_summary.sort_values(
        "Downtime_Hours",
        ascending=False
    )


    # ========================================================
    # DOWNTIME CHART
    # ========================================================

    downtime_chart = (

        downtime_summary[
            [
                "Machine_Label",
                "Downtime_Hours"
            ]
        ]

        .set_index("Machine_Label")

    )


    st.bar_chart(
        downtime_chart
    )


    # ========================================================
    # DOWNTIME SUMMARY TABLE
    # ========================================================

    st.markdown("#### Downtime Summary")


    downtime_display = downtime_summary[
        [
            "Plant",
            "Machine",
            "Downtime_Hours"
        ]
    ].copy()
    st.dataframe(
        downtime_display,
        use_container_width=True,
        hide_index=True
    )
else:
     st.info(
        "No downtime data available for the selected filters."
    )
     # ============================================================
# BUSINESS IMPACT / FINANCIAL ANALYSIS
# ============================================================

st.markdown("---")

st.header("💰 Estimated Business Impact")


# ============================================================
# LOAD DATA DIRECTLY FROM DATABASE
# ============================================================

financial_production = pd.read_sql_query(
    """
    SELECT
        Date,
        Plant,
        Machine,
        Target_Production,
        Actual_Production
    FROM production
    """,
    sql_connection
)


financial_quality = pd.read_sql_query(
    """
    SELECT
        Date,
        Plant,
        Machine,
        Units_Produced,
        Defective_Units
    FROM quality
    """,
    sql_connection
)


financial_downtime = pd.read_sql_query(
    """
    SELECT
        Date,
        Plant,
        Machine,
        Downtime_Hours
    FROM downtime
    """,
    sql_connection
)


# ============================================================
# CONVERT DATES
# ============================================================

financial_production["Date"] = pd.to_datetime(
    financial_production["Date"]
)

financial_quality["Date"] = pd.to_datetime(
    financial_quality["Date"]
)

financial_downtime["Date"] = pd.to_datetime(
    financial_downtime["Date"]
)


# ============================================================
# APPLY DATE FILTER
# ============================================================

if isinstance(selected_dates, tuple) and len(selected_dates) == 2:

    start_date = pd.to_datetime(
        selected_dates[0]
    )

    end_date = pd.to_datetime(
        selected_dates[1]
    )


    financial_production = financial_production[
        (
            financial_production["Date"] >= start_date
        )
        &
        (
            financial_production["Date"] <= end_date
        )
    ]


    financial_quality = financial_quality[
        (
            financial_quality["Date"] >= start_date
        )
        &
        (
            financial_quality["Date"] <= end_date
        )
    ]


    financial_downtime = financial_downtime[
        (
            financial_downtime["Date"] >= start_date
        )
        &
        (
            financial_downtime["Date"] <= end_date
        )
    ]


# ============================================================
# APPLY PLANT FILTER
# ============================================================

if selected_plant != "All":

    financial_production = financial_production[
        financial_production["Plant"] == selected_plant
    ]

    financial_quality = financial_quality[
        financial_quality["Plant"] == selected_plant
    ]

    financial_downtime = financial_downtime[
        financial_downtime["Plant"] == selected_plant
    ]


# ============================================================
# APPLY MACHINE FILTER
# ============================================================

if selected_machine != "All":

    financial_production = financial_production[
        financial_production["Machine"] == selected_machine
    ]

    financial_quality = financial_quality[
        financial_quality["Machine"] == selected_machine
    ]

    financial_downtime = financial_downtime[
        financial_downtime["Machine"] == selected_machine
    ]


# ============================================================
# CALCULATE TOTALS
# ============================================================

total_target = financial_production[
    "Target_Production"
].sum()

total_actual = financial_production[
    "Actual_Production"
].sum()


total_missed_production = max(
    total_target - total_actual,
    0
)


total_defective_units = financial_quality[
    "Defective_Units"
].sum()


total_downtime_hours = financial_downtime[
    "Downtime_Hours"
].sum()


# ============================================================
# CALCULATE FINANCIAL IMPACT
# ============================================================

downtime_cost = (

    total_downtime_hours

    * cost_per_downtime_hour

)


defect_cost = (

    total_defective_units

    * cost_per_defective_unit

)


missed_production_cost = (

    total_missed_production

    * value_per_missed_unit

)


total_business_impact = (

    downtime_cost

    + defect_cost

    + missed_production_cost

)


# ============================================================
# DISPLAY FINANCIAL KPIs
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Downtime Cost",
        f"₹{downtime_cost:,.0f}"
    )


with col2:

    st.metric(
        "Defect Cost",
        f"₹{defect_cost:,.0f}"
    )


with col3:

    st.metric(
        "Missed Production Value",
        f"₹{missed_production_cost:,.0f}"
    )


with col4:

    st.metric(
        "Total Estimated Impact",
        f"₹{total_business_impact:,.0f}"
    )


# ============================================================
# IMPACT BREAKDOWN
# ============================================================

st.markdown("#### 💵 Impact Breakdown")


impact_data = pd.DataFrame({

    "Impact Category": [

        "Downtime",

        "Defective Units",

        "Missed Production"

    ],

    "Estimated Cost (₹)": [

        downtime_cost,

        defect_cost,

        missed_production_cost

    ]

})


st.bar_chart(

    impact_data.set_index(
        "Impact Category"
    )

)


# ============================================================
# SUPPORTING METRICS
# ============================================================

st.markdown("#### Operational Loss Indicators")


loss_col1, loss_col2, loss_col3 = st.columns(3)


with loss_col1:

    st.metric(
        "Total Downtime",
        f"{total_downtime_hours:,.2f} hrs"
    )


with loss_col2:

    st.metric(
        "Defective Units",
        f"{total_defective_units:,.0f}"
    )


with loss_col3:

    st.metric(
        "Missed Production",
        f"{total_missed_production:,.0f} units"
    )
    # ============================================================
# MANAGEMENT RECOMMENDATIONS
# ============================================================

st.markdown("---")

st.header("🧠 Management Recommendations")


if not priority_result.empty:

    # --------------------------------------------------------
    # TOP PRIORITY MACHINE
    # --------------------------------------------------------

    top_machine = priority_result.iloc[0]

    top_plant = top_machine["Plant"]

    top_machine_name = top_machine["Machine"]

    top_action = top_machine["Primary_Action"]

    top_risk = top_machine["Operational_Risk_Score"]

    top_production_gap = top_machine[
        "Production_Shortfall"
    ]

    top_defect_rate = top_machine[
        "Defect_Rate"
    ]

    top_downtime = top_machine[
        "Downtime_Hours"
    ]


    # --------------------------------------------------------
    # MAIN RECOMMENDATION
    # --------------------------------------------------------

    if top_action == "Investigate downtime":

        recommendation = (

            f"Prioritize investigation of downtime on "
            f"{top_plant} - {top_machine_name}. "
            f"The machine recorded {top_downtime:.2f} hours "
            f"of downtime and has an operational risk score "
            f"of {top_risk:.2f}. Review recurring stoppages, "
            f"maintenance history, and machine availability."
        )


    elif top_action == "Investigate quality":

        recommendation = (

            f"Prioritize quality investigation on "
            f"{top_plant} - {top_machine_name}. "
            f"The machine has a defect rate of "
            f"{top_defect_rate:.2f}% and an operational risk "
            f"score of {top_risk:.2f}. Review process conditions, "
            f"quality deviations, and inspection records."
        )


    elif top_action == "Investigate production":

        recommendation = (

            f"Prioritize production investigation on "
            f"{top_plant} - {top_machine_name}. "
            f"The machine has a production shortfall of "
            f"{top_production_gap:.2f}% and an operational "
            f"risk score of {top_risk:.2f}. Review operating "
            f"conditions, throughput constraints, and "
            f"production planning."
        )


    else:

        recommendation = (

            f"{top_plant} - {top_machine_name} is currently "
            f"the highest-priority machine under the selected "
            f"filters. Continue monitoring its operational "
            f"performance."
        )


    # --------------------------------------------------------
    # DISPLAY MAIN RECOMMENDATION
    # --------------------------------------------------------

    st.info(
        recommendation
    )


    # --------------------------------------------------------
    # ADDITIONAL MANAGEMENT ACTIONS
    # --------------------------------------------------------

    st.markdown("#### Recommended Actions")


    if top_action == "Investigate downtime":

        st.markdown(
            """
            - Review machine downtime history and recurring stoppages.
            - Check preventive maintenance compliance.
            - Investigate whether downtime is concentrated in specific operating periods.
            """
        )


    elif top_action == "Investigate quality":

        st.markdown(
            """
            - Review defect patterns and process conditions.
            - Identify recurring quality deviations.
            - Check inspection and process-control records.
            """
        )


    elif top_action == "Investigate production":

        st.markdown(
            """
            - Review production target versus actual output.
            - Investigate throughput constraints.
            - Check operating conditions and production scheduling.
            """
        )


    else:

        st.markdown(
            """
            - Continue monitoring the machine.
            - Review the risk trend periodically.
            - Investigate if the risk score begins to increase.
            """
        )


else:

    st.info(
        "No recommendations available for the selected filters."
    )
# ============================================================
# EXECUTIVE MANAGEMENT SUMMARY
# ============================================================

st.markdown("---")

st.header("📋 Executive Management Summary")


# ------------------------------------------------------------
# OVERALL PRODUCTION PERFORMANCE
# ------------------------------------------------------------

total_target_summary = (
    filtered_production["Target_Production"].sum()
)

total_actual_summary = (
    filtered_production["Actual_Production"].sum()
)

if total_target_summary > 0:

    overall_achievement_summary = (
        total_actual_summary
        / total_target_summary
        * 100
    )

else:

    overall_achievement_summary = 0


production_gap_summary = (
    100 - overall_achievement_summary
)


# ------------------------------------------------------------
# WORST PLANT
# ------------------------------------------------------------

if len(plant_production) > 0:

    summary_worst_plant = (
        plant_production["Achievement"].idxmin()
    )

    summary_worst_plant_rate = (
        plant_production.loc[
            summary_worst_plant,
            "Achievement"
        ]
    )

else:

    summary_worst_plant = "N/A"
    summary_worst_plant_rate = 0


# ------------------------------------------------------------
# MAIN DOWNTIME DRIVER
# ------------------------------------------------------------

if len(downtime_analysis) > 0:

    summary_top_downtime = (
        downtime_analysis.index[0]
    )

    summary_top_downtime_share = (
        downtime_analysis.iloc[0]["Share_of_Total_%"]
    )

else:

    summary_top_downtime = "N/A"
    summary_top_downtime_share = 0


# ------------------------------------------------------------
# WORST QUALITY MACHINE
# ------------------------------------------------------------

if len(machine_quality) > 0:

    summary_worst_machine = (
        machine_quality.index[0]
    )

    summary_worst_machine_rate = (
        machine_quality.iloc[0]["Defect_Rate"]
    )

else:

    summary_worst_machine = "N/A"
    summary_worst_machine_rate = 0


# ------------------------------------------------------------
# MANAGEMENT SUMMARY CARDS
# ------------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Production Achievement",
        f"{overall_achievement_summary:.2f}%"
    )


with col2:

    st.metric(
        "Production Gap",
        f"{production_gap_summary:.2f}%"
    )


with col3:

    st.metric(
        "Top Downtime Cause",
        summary_top_downtime
    )


with col4:

    st.metric(
        "Highest Defect Machine",
        summary_worst_machine
    )


# ------------------------------------------------------------
# MANAGEMENT INSIGHTS
# ------------------------------------------------------------

st.subheader("🔎 Key Management Insights")


st.info(
    f"**Production:** Overall production achievement is "
    f"**{overall_achievement_summary:.2f}%** of target, "
    f"representing a **{production_gap_summary:.2f} percentage "
    f"point gap** from the target."
)


st.warning(
    f"**Production Priority:** "
    f"**{summary_worst_plant}** has the lowest production "
    f"achievement at **{summary_worst_plant_rate:.2f}%**. "
    f"Investigate production losses and operational "
    f"bottlenecks at this plant."
)


st.warning(
    f"**Downtime Priority:** "
    f"**{summary_top_downtime}** contributes "
    f"**{summary_top_downtime_share:.2f}%** of total downtime. "
    f"This should be prioritized for root-cause investigation."
)


st.error(
    f"**Quality Priority:** "
    f"**{summary_worst_machine}** has the highest defect rate "
    f"at **{summary_worst_machine_rate:.2f}%**. "
    f"Review machine operating conditions, maintenance history "
    f"and process parameters."
)


# ------------------------------------------------------------
# FINANCIAL IMPACT SUMMARY
# ------------------------------------------------------------

st.success(
    f"💰 **Estimated Business Impact:** "
    f"The selected period has an estimated operational impact "
    f"of **₹{total_business_impact:,.0f}**, based on the "
    f"user-defined financial assumptions."
)


# ------------------------------------------------------------
# FINAL MANAGEMENT ACTION
# ------------------------------------------------------------

st.subheader("🎯 Recommended Management Focus")


st.markdown(
    f"""
**Priority 1 — Downtime:** Reduce **{summary_top_downtime}**
through targeted root-cause analysis and corrective maintenance.

**Priority 2 — Quality:** Investigate **{summary_worst_machine}**
because it currently has the highest defect rate.

**Priority 3 — Production:** Investigate **{summary_worst_plant}**
to identify the operational factors responsible for the
production achievement gap.

**Financial Opportunity:** Focus improvement efforts on the
largest sources of operational loss first to maximize the
potential financial benefit.
"""
)
# ============================================================
# KPI CARDS
# ============================================================

st.markdown("---")

st.subheader("Executive KPIs")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "📉 Production Achievement",
        f"{achievement:.2f}%"
    )

with col2:

    st.metric(
        "⚙️ Highest Downtime Machine",
        downtime_machine
    )

with col3:

    st.metric(
        "⏱️ Total Downtime",
        f"{total_downtime:,.1f} hrs"
    )


col4, col5, col6 = st.columns(3)

with col4:

    st.metric(
        "💰 Estimated Production Loss",
        f"₹{estimated_loss / 100000:.2f} L"
    )

with col5:

    st.metric(
        "📦 Highest Defect Product",
        worst_product
    )

with col6:

    st.metric(
        "⚠️ Defect Rate",
        f"{defect_rate:.2f}%"
    )


# ============================================================
# PRODUCTION CHART
# ============================================================

st.markdown("---")

st.header("📉 Production Achievement")

production_chart = (
    filtered_production
    .groupby("Plant")
    .agg(
        Target=("Target_Production", "sum"),
        Actual=("Actual_Production", "sum")
    )
)

production_chart["Achievement"] = (
    production_chart["Actual"]
    / production_chart["Target"]
    * 100
)

st.bar_chart(
    production_chart["Achievement"]
)


# ============================================================
# DOWNTIME CHART
# ============================================================

st.markdown("---")

st.header("⚙️ Downtime by Machine")

downtime_chart = (
    filtered_downtime
    .groupby("Machine")["Downtime_Hours"]
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(
    downtime_chart
)


# ============================================================
# QUALITY CHART
# ============================================================

st.markdown("---")

st.header("📦 Defect Rate by Product")

quality_chart = (
    filtered_quality
    .groupby("Product")
    .agg(
        Produced=("Units_Produced", "sum"),
        Defective=("Defective_Units", "sum")
    )
)

quality_chart["Defect Rate"] = (
    quality_chart["Defective"]
    / quality_chart["Produced"]
    * 100
)

quality_chart = quality_chart[
    "Defect Rate"
].sort_values(ascending=False)

st.bar_chart(
    quality_chart
)
# ============================================================
# PRODUCTION TREND OVER TIME
# ============================================================

st.markdown("---")

st.header("📈 Production Performance Over Time")

# Convert Date column to datetime
filtered_production["Date"] = pd.to_datetime(
    filtered_production["Date"]
)

# Group production by date
daily_production = (
    filtered_production
    .groupby("Date")
    .agg(
        Target=("Target_Production", "sum"),
        Actual=("Actual_Production", "sum")
    )
)

# Calculate daily achievement
daily_production["Achievement"] = (
    daily_production["Actual"]
    / daily_production["Target"]
    * 100
)

# Sort chronologically
daily_production = daily_production.sort_index()

# Display trend
st.line_chart(
    daily_production["Achievement"]
)

st.caption(
    "Daily production achievement = "
    "Actual Production ÷ Target Production × 100"
)
# ============================================================
# DOWNTIME TREND OVER TIME
# ============================================================

st.markdown("---")

st.header("📈 Downtime Trend Over Time")

# Convert Date column to datetime
filtered_downtime["Date"] = pd.to_datetime(
    filtered_downtime["Date"]
)

# Group downtime by date
daily_downtime = (
    filtered_downtime
    .groupby("Date")["Downtime_Hours"]
    .sum()
    .sort_index()
)

# Display downtime trend
st.line_chart(
    daily_downtime
)

st.caption(
    "Daily total downtime hours based on the selected filters."
)
# ============================================================
# DOWNTIME INSIGHT
# ============================================================

st.markdown("---")

st.header("🚨 Operational Insight")

if len(filtered_downtime) > 0:

    top_machine = (
        filtered_downtime
        .groupby("Machine")["Downtime_Hours"]
        .sum()
        .idxmax()
    )

    top_machine_hours = (
        filtered_downtime
        .groupby("Machine")["Downtime_Hours"]
        .sum()
        .max()
    )

    top_reason = (
        filtered_downtime[
            filtered_downtime["Machine"] == top_machine
        ]
        .groupby("Downtime_Reason")["Downtime_Hours"]
        .sum()
        .idxmax()
    )

    st.write(
        f"**{top_machine}** has the highest downtime "
        f"at **{top_machine_hours:,.2f} hours**."
    )

    st.write(
        f"The dominant downtime reason is "
        f"**{top_reason}**."
    )

    st.write(
        f"Estimated production value at risk: "
        f"**₹{top_machine_hours * units_per_hour * value_per_unit:,.2f}**."
    )


# ============================================================
# QUALITY INSIGHT
# ============================================================

st.markdown("---")

st.header("🔍 Quality Insight")

if len(filtered_quality) > 0:

    top_product = (
        filtered_quality
        .groupby("Product")
        .apply(
            lambda x:
            x["Defective_Units"].sum()
            / x["Units_Produced"].sum() * 100
        )
        .idxmax()
    )

    top_product_rate = (
        filtered_quality[
            filtered_quality["Product"] == top_product
        ]["Defective_Units"].sum()
        /
        filtered_quality[
            filtered_quality["Product"] == top_product
        ]["Units_Produced"].sum()
        * 100
    )

    st.write(
        f"**{top_product}** has the highest defect rate "
        f"at **{top_product_rate:.2f}%**."
    )
# ============================================================
# AUTOMATED BUSINESS RECOMMENDATIONS
# ============================================================

st.markdown("---")

st.header("🤖 PlantPulse Recommendations")

# ------------------------------------------------------------
# PRODUCTION RECOMMENDATION
# ------------------------------------------------------------

if achievement < 90:

    st.warning(
        f"🔴 **Production Alert — {selected_plant}**\n\n"
        f"Production achievement is **{achievement:.2f}%**, "
        f"which is below the 90% monitoring threshold.\n\n"
        f"**Recommended action:** Investigate production losses, "
        f"downtime patterns and machine-level bottlenecks."
    )

else:

    st.success(
        f"🟢 **Production Status — {selected_plant}**\n\n"
        f"Production achievement is **{achievement:.2f}%**.\n\n"
        f"Continue monitoring production performance."
    )


# ------------------------------------------------------------
# DOWNTIME RECOMMENDATION
# ------------------------------------------------------------

if total_downtime > 100:

    st.error(
        f"🔴 **Maintenance Priority — {downtime_machine}**\n\n"
        f"The selected scope contains **"
        f"{total_downtime:,.1f} hours** of downtime.\n\n"
        f"The highest downtime machine is **"
        f"{downtime_machine}**.\n\n"
        f"Dominant downtime cause: **{top_reason}**.\n\n"
        f"**Recommended action:** Prioritize preventive maintenance "
        f"and investigate recurring failures associated with "
        f"{top_reason.lower()}."
    )

elif total_downtime > 50:

    st.warning(
        f"🟠 **Maintenance Watch — {downtime_machine}**\n\n"
        f"Downtime totals **{total_downtime:,.1f} hours**.\n\n"
        f"**Recommended action:** Review maintenance records "
        f"and monitor the machine for recurring downtime."
    )

else:

    st.success(
        f"🟢 **Downtime Status**\n\n"
        f"Downtime is currently **{total_downtime:,.1f} hours** "
        f"within the selected scope."
    )


# ------------------------------------------------------------
# QUALITY RECOMMENDATION
# ------------------------------------------------------------

if defect_rate > 5:

    st.error(
        f"🔴 **Quality Priority — {worst_product}**\n\n"
        f"The defect rate is **{defect_rate:.2f}%**, "
        f"which exceeds the 5% quality threshold.\n\n"
        f"**Recommended action:** Investigate process conditions, "
        f"machine settings and recurring defect patterns for "
        f"{worst_product}."
    )

elif defect_rate > 3:

    st.warning(
        f"🟠 **Quality Watch — {worst_product}**\n\n"
        f"The defect rate is **{defect_rate:.2f}%**.\n\n"
        f"**Recommended action:** Monitor quality performance "
        f"and investigate the main contributing machine."
    )

else:

    st.success(
        f"🟢 **Quality Status**\n\n"
        f"Current defect rate is **{defect_rate:.2f}%**."
    )


# ------------------------------------------------------------
# FINANCIAL IMPACT
# ------------------------------------------------------------

if estimated_loss > 1000000:

    st.error(
        f"💰 **Financial Priority**\n\n"
        f"Estimated production value at risk is "
        f"**₹{estimated_loss / 100000:.2f} lakh**.\n\n"
        f"Reducing downtime should be treated as a "
        f"high-priority operational improvement opportunity."
    )

elif estimated_loss > 500000:

    st.warning(
        f"💰 **Financial Watch**\n\n"
        f"Estimated production value at risk is "
        f"**₹{estimated_loss / 100000:.2f} lakh**."
    )

# ============================================================
# FILTER STATUS
# ============================================================

st.markdown("---")

st.caption(
    f"Current filters → "
    f"Plant: {selected_plant} | "
    f"Machine: {selected_machine} | "
    f"Product: {selected_product}"
)


# ============================================================
# CLOSE DATABASE
# ============================================================

connection.close()
# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "PlantPulse | Operational Intelligence & Decision Support Dashboard"
)