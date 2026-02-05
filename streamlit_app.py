import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Global Seismic Trends",
    layout="wide"
)

# ---------------- LOAD DATA (MYSQL LOCAL / CSV CLOUD) ----------------
@st.cache_data
def load_data():
    try:
        # Try MySQL (LOCAL MACHINE ONLY)
        import mysql.connector

        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="guvi_project_01"
        )
        df = pd.read_sql("SELECT * FROM earthquakes_raw", conn)
        conn.close()

        st.success("✅ Data loaded from MySQL (Local Mode)")
        return df

    except Exception:
        # Fallback for Streamlit Cloud
        df = pd.read_csv("raw_earthquake_data.csv")
        st.warning("⚠️ Data loaded from CSV (Cloud Demo Mode)")
        return df


# ---------------- LOAD DATA ----------------
df = load_data()

# ---------------- PREPROCESS ----------------
df['time'] = pd.to_datetime(df['time'], unit='ms', errors='coerce')
df['year'] = df['time'].dt.year
df['month'] = df['time'].dt.month
df['day'] = df['time'].dt.day_name()

df['alert'] = df['alert'].fillna("none").str.lower()

df = df.dropna(subset=['mag', 'depth_km'])

# ---------------- TITLE ----------------
st.title("🌍 Global Seismic Trends: Data-Driven Earthquake Insights")
st.markdown("Interactive SQL-style analytics dashboard (MySQL local | CSV cloud)")

# ---------------- KPI METRICS ----------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Earthquakes", len(df))
c2.metric("Avg Magnitude", round(df['mag'].mean(), 2))
c3.metric("Avg Depth (km)", round(df['depth_km'].mean(), 2))
c4.metric("Tsunamis", int(df['tsunami'].sum()))

# ======================================================
# =============== SQL QUESTION PANELS ===================
# ======================================================

st.subheader("📌 Analytical Questions (Click to View SQL + Output)")

SQL_QUERIES = {
    "Top 10 Strongest Earthquakes": """
SELECT place, mag, depth_km
FROM earthquakes_raw
ORDER BY mag DESC
LIMIT 10;
""",

    "Top 10 Deepest Earthquakes": """
SELECT place, depth_km, mag
FROM earthquakes_raw
ORDER BY depth_km DESC
LIMIT 10;
""",

    "Earthquakes Per Year": """
SELECT YEAR(FROM_UNIXTIME(time/1000)) AS year,
COUNT(*) AS count
FROM earthquakes_raw
GROUP BY year;
""",

    "Earthquakes by Alert Level": """
SELECT alert, COUNT(*) AS count
FROM earthquakes_raw
GROUP BY alert;
""",

    "Average Magnitude by Type": """
SELECT magType, ROUND(AVG(mag),2) AS avg_magnitude
FROM earthquakes_raw
GROUP BY magType;
""",

    "Tsunamis Triggered Per Year": """
SELECT YEAR(FROM_UNIXTIME(time/1000)) AS year,
COUNT(*) AS tsunami_count
FROM earthquakes_raw
WHERE tsunami = 1
GROUP BY year;
""",

    "Reviewed vs Automatic Events": """
SELECT status, COUNT(*) AS count
FROM earthquakes_raw
GROUP BY status;
""",

    "High-Risk Earthquakes (Mag ≥ 7)": """
SELECT place, mag, depth_km
FROM earthquakes_raw
WHERE mag >= 7
ORDER BY mag DESC;
"""
}

# ---------------- DISPLAY QUESTIONS ----------------
for question, query in SQL_QUERIES.items():
    with st.expander(f"📍 {question}"):
        st.markdown("**SQL Query (Conceptual)**")
        st.code(query, language="sql")

        # Execute using pandas (cloud-safe)
        if "FROM_UNIXTIME" in query:
            if "GROUP BY year" in query:
                result_df = df.groupby('year').size().reset_index(name='count')
            else:
                result_df = df
        elif "alert" in query:
            result_df = df.groupby('alert').size().reset_index(name='count')
        elif "magType" in query:
            result_df = df.groupby('magType')['mag'].mean().round(2).reset_index()
        elif "tsunami = 1" in query:
            result_df = (
                df[df['tsunami'] == 1]
                .groupby('year')
                .size()
                .reset_index(name='tsunami_count')
            )
        elif "status" in query:
            result_df = df.groupby('status').size().reset_index(name='count')
        elif "mag >= 7" in query:
            result_df = df[df['mag'] >= 7][['place', 'mag', 'depth_km']]
        else:
            result_df = df[['place', 'mag', 'depth_km']].sort_values(by='mag', ascending=False).head(10)

        st.dataframe(result_df, use_container_width=True)

        if result_df.shape[1] == 2:
            fig = px.bar(
                result_df,
                x=result_df.columns[0],
                y=result_df.columns[1],
                title=question
            )
            st.plotly_chart(fig, use_container_width=True)

# ---------------- RAW DATA PREVIEW ----------------
st.subheader("📄 Sample Earthquake Records")
st.dataframe(df.head(300), use_container_width=True)

# ---------------- END ----------------
st.success("✅ Global Seismic Trends Dashboard Loaded Successfully")