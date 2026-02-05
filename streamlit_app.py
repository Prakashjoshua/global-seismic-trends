import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Global Seismic Trends", layout="wide")

# ---------------- DB CONNECTION ----------------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="guvi_project_01"
    )

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM earthquakes_raw", conn)
    conn.close()
    return df

# ---------------- TITLE ----------------
st.title("🌍 Global Seismic Trends: Data-Driven Earthquake Insights")
st.markdown("Click any question to view the SQL query and its live output")

# ---------------- LOAD ----------------
df = load_data()

# ---------------- PREPROCESS ----------------
df['time'] = pd.to_datetime(df['time'], unit='ms', errors='coerce')
df['year'] = df['time'].dt.year
df['alert'] = df['alert'].fillna("none").str.lower()
df = df.dropna(subset=['mag', 'depth_km'])

# ---------------- KPI ----------------
c1, c2, c3 = st.columns(3)
c1.metric("Total Earthquakes", len(df))
c2.metric("Avg Magnitude", round(df['mag'].mean(), 2))
c3.metric("Avg Depth (km)", round(df['depth_km'].mean(), 2))

# ======================================================
# =============== SQL QUESTIONS ========================
# ======================================================

SQL_SECTIONS = {

"🟦 Magnitude & Depth Analysis": {
"1️⃣ Top 10 Strongest Earthquakes": """
SELECT place, mag, depth_km
FROM earthquakes_raw
ORDER BY mag DESC
LIMIT 10;
""",

"2️⃣ Top 10 Deepest Earthquakes": """
SELECT place, depth_km, mag
FROM earthquakes_raw
ORDER BY depth_km DESC
LIMIT 10;
""",

"3️⃣ Shallow earthquakes (<50 km) with mag > 7.5": """
SELECT place, mag, depth_km
FROM earthquakes_raw
WHERE depth_km < 50 AND mag > 7.5;
""",

"4️⃣ Average depth by magnitude type": """
SELECT magType, ROUND(AVG(depth_km),2) AS avg_depth
FROM earthquakes_raw
GROUP BY magType;
""",

"5️⃣ Average magnitude by magnitude type": """
SELECT magType, ROUND(AVG(mag),2) AS avg_mag
FROM earthquakes_raw
GROUP BY magType;
"""
},

"🟩 Time-Based Analysis": {
"6️⃣ Earthquakes per year": """
SELECT YEAR(FROM_UNIXTIME(time/1000)) AS year,
COUNT(*) AS count
FROM earthquakes_raw
GROUP BY year
ORDER BY year;
""",

"7️⃣ Month with highest earthquakes": """
SELECT MONTH(FROM_UNIXTIME(time/1000)) AS month,
COUNT(*) AS count
FROM earthquakes_raw
GROUP BY month
ORDER BY count DESC
LIMIT 1;
""",

"8️⃣ Day of week with most earthquakes": """
SELECT DAYNAME(FROM_UNIXTIME(time/1000)) AS day,
COUNT(*) AS count
FROM earthquakes_raw
GROUP BY day;
""",

"9️⃣ Earthquakes per hour": """
SELECT HOUR(FROM_UNIXTIME(time/1000)) AS hour,
COUNT(*) AS count
FROM earthquakes_raw
GROUP BY hour
ORDER BY hour;
""",

"🔟 Most active reporting network": """
SELECT net, COUNT(*) AS reports
FROM earthquakes_raw
GROUP BY net
ORDER BY reports DESC
LIMIT 1;
"""
},

"🟨 Tsunami & Alert Analysis": {
"1️⃣1️⃣ Tsunamis per year": """
SELECT YEAR(FROM_UNIXTIME(time/1000)) AS year,
COUNT(*) AS tsunami_count
FROM earthquakes_raw
WHERE tsunami=1
GROUP BY year;
""",

"1️⃣2️⃣ Earthquakes by alert level": """
SELECT alert, COUNT(*) AS count
FROM earthquakes_raw
GROUP BY alert;
""",

"1️⃣3️⃣ Average magnitude by alert level": """
SELECT alert, ROUND(AVG(mag),2) AS avg_mag
FROM earthquakes_raw
GROUP BY alert;
"""
},

"🟥 Event Quality & Metrics": {
"1️⃣4️⃣ Reviewed vs Automatic events": """
SELECT status, COUNT(*) AS count
FROM earthquakes_raw
GROUP BY status;
""",

"1️⃣5️⃣ Events by type": """
SELECT eventType, COUNT(*) AS count
FROM earthquakes_raw
GROUP BY eventType;
""",

"1️⃣6️⃣ Average RMS and GAP": """
SELECT ROUND(AVG(rms),2) AS avg_rms,
ROUND(AVG(gap),2) AS avg_gap
FROM earthquakes_raw;
""",

"1️⃣7️⃣ High station coverage events (nst > 50)": """
SELECT place, mag, nst
FROM earthquakes_raw
WHERE nst > 50;
""",

"1️⃣8️⃣ Least reliable events": """
SELECT place, rms, gap
FROM earthquakes_raw
ORDER BY rms DESC, gap DESC
LIMIT 10;
"""
},

"🟪 Location & Pattern Analysis": {
"1️⃣9️⃣ Deep-focus earthquakes (>300 km)": """
SELECT place, depth_km, mag
FROM earthquakes_raw
WHERE depth_km > 300;
""",

"2️⃣0️⃣ Shallow vs Deep earthquake ratio": """
SELECT
SUM(CASE WHEN depth_km < 70 THEN 1 ELSE 0 END) AS shallow,
SUM(CASE WHEN depth_km > 300 THEN 1 ELSE 0 END) AS deep
FROM earthquakes_raw;
""",

"2️⃣1️⃣ Average depth near equator (±5°)": """
SELECT ROUND(AVG(depth_km),2) AS avg_depth
FROM earthquakes_raw
WHERE latitude BETWEEN -5 AND 5;
""",

"2️⃣2️⃣ Strong earthquakes (>6.5) by place": """
SELECT place, COUNT(*) AS count
FROM earthquakes_raw
WHERE mag > 6.5
GROUP BY place
ORDER BY count DESC
LIMIT 10;
""",

"2️⃣3️⃣ Most significant earthquakes": """
SELECT place, mag, sig
FROM earthquakes_raw
ORDER BY sig DESC
LIMIT 10;
"""
},

"⬛ Advanced & Risk Analysis": {
"2️⃣4️⃣ Year-over-year growth": """
SELECT year,
count,
count - LAG(count) OVER (ORDER BY year) AS growth
FROM (
SELECT YEAR(FROM_UNIXTIME(time/1000)) AS year,
COUNT(*) AS count
FROM earthquakes_raw
GROUP BY year
) t;
""",

"2️⃣5️⃣ Avg magnitude: tsunami vs non-tsunami": """
SELECT tsunami, ROUND(AVG(mag),2) AS avg_mag
FROM earthquakes_raw
GROUP BY tsunami;
""",

"2️⃣6️⃣ Events with high depth error": """
SELECT place, depth_km, depthError
FROM earthquakes_raw
ORDER BY depthError DESC
LIMIT 10;
""",

"2️⃣7️⃣ Network-wise average magnitude": """
SELECT net, ROUND(AVG(mag),2) AS avg_mag
FROM earthquakes_raw
GROUP BY net;
""",

"2️⃣8️⃣ Monthly earthquake trend": """
SELECT YEAR(FROM_UNIXTIME(time/1000)) AS year,
MONTH(FROM_UNIXTIME(time/1000)) AS month,
COUNT(*) AS count
FROM earthquakes_raw
GROUP BY year, month
ORDER BY year, month;
""",

"2️⃣9️⃣ Earthquake risk classification": """
SELECT
CASE
WHEN mag>=7 THEN 'High Risk'
WHEN mag BETWEEN 5 AND 6.9 THEN 'Moderate Risk'
ELSE 'Low Risk'
END AS risk_level,
COUNT(*) AS count
FROM earthquakes_raw
GROUP BY risk_level;
""",

"3️⃣0️⃣ Tsunami-prone high magnitude events": """
SELECT place, mag, tsunami
FROM earthquakes_raw
WHERE mag > 7 AND tsunami=1;
"""
}
}

# ---------------- DISPLAY QUESTIONS ----------------
for section, queries in SQL_SECTIONS.items():
    st.subheader(section)

    for question, query in queries.items():
        with st.expander(question):
            st.code(query, language="sql")

            conn = get_connection()
            result_df = pd.read_sql(query, conn)
            conn.close()

            st.dataframe(result_df, use_container_width=True)

            if result_df.shape[1] == 2:
                fig = px.bar(
                    result_df,
                    x=result_df.columns[0],
                    y=result_df.columns[1],
                    title=question
                )
                st.plotly_chart(fig, use_container_width=True)

# ---------------- END ----------------
st.success("✅ All 30 SQL analytical questions loaded successfully")