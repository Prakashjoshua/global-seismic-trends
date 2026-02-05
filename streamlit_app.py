import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Global Seismic Trends – SQL Queries",
    layout="wide"
)

# ---------------- TITLE ----------------
st.title("🌍 Global Seismic Trends")
st.caption("30 Analytical SQL Questions | Click a question to view the SQL query")

# ---------------- HELPER ----------------
def show_sql(qno, title, sql):
    with st.expander(f"{qno}. {title}"):
        st.markdown("**SQL Query**")
        st.code(sql, language="sql")

# =====================================================
# ===================== 30 SQL QUESTIONS ===============
# =====================================================

# 🔹 Magnitude & Depth Analysis
show_sql(1, "Top 15 strongest earthquakes",
"""
SELECT place, mag, depth_km
FROM earthquakes_raw
ORDER BY mag DESC
LIMIT 15;
""")

show_sql(2, "Top 15 deepest earthquakes",
"""
SELECT place, depth_km, mag
FROM earthquakes_raw
ORDER BY depth_km DESC
LIMIT 15;
""")

show_sql(3, "Shallow earthquakes (<50 km) with magnitude > 7.5",
"""
SELECT *
FROM earthquakes_raw
WHERE depth_km < 50 AND mag > 7.5
LIMIT 15;
""")

show_sql(4, "Average depth of all earthquakes",
"""
SELECT AVG(depth_km) AS avg_depth
FROM earthquakes_raw;
""")

show_sql(5, "Average magnitude by magnitude type",
"""
SELECT magType, AVG(mag) AS avg_magnitude
FROM earthquakes_raw
GROUP BY magType;
""")

# 🔹 Time Analysis
show_sql(6, "Year with the highest number of earthquakes",
"""
SELECT YEAR(FROM_UNIXTIME(time/1000)) AS year, COUNT(*) AS count
FROM earthquakes_raw
GROUP BY year
ORDER BY count DESC
LIMIT 1;
""")

show_sql(7, "Month with the highest number of earthquakes",
"""
SELECT MONTH(FROM_UNIXTIME(time/1000)) AS month, COUNT(*) AS count
FROM earthquakes_raw
GROUP BY month
ORDER BY count DESC
LIMIT 1;
""")

show_sql(8, "Day of the week with most earthquakes",
"""
SELECT DAYNAME(FROM_UNIXTIME(time/1000)) AS day, COUNT(*) AS count
FROM earthquakes_raw
GROUP BY day
ORDER BY count DESC
LIMIT 1;
""")

show_sql(9, "Earthquake count per hour",
"""
SELECT HOUR(FROM_UNIXTIME(time/1000)) AS hour, COUNT(*) AS count
FROM earthquakes_raw
GROUP BY hour;
""")

show_sql(10, "Most active seismic network",
"""
SELECT net, COUNT(*) AS count
FROM earthquakes_raw
GROUP BY net
ORDER BY count DESC
LIMIT 1;
""")

# 🔹 Quality & Event Type
show_sql(11, "Reviewed vs Automatic events",
"""
SELECT status, COUNT(*) AS count
FROM earthquakes_raw
GROUP BY status;
""")

show_sql(12, "Number of earthquakes by event type",
"""
SELECT eventType, COUNT(*) AS count
FROM earthquakes_raw
GROUP BY eventType;
""")

show_sql(13, "Number of earthquakes by data type",
"""
SELECT types, COUNT(*) AS count
FROM earthquakes_raw
GROUP BY types;
""")

show_sql(14, "High station coverage earthquakes (nst > 50)",
"""
SELECT *
FROM earthquakes_raw
WHERE nst > 50
LIMIT 15;
""")

show_sql(15, "Least reliable earthquakes (high RMS and GAP)",
"""
SELECT *
FROM earthquakes_raw
ORDER BY rms DESC, gap DESC
LIMIT 15;
""")

# 🔹 Tsunami & Alerts
show_sql(16, "Total tsunami events",
"""
SELECT COUNT(*) AS tsunami_events
FROM earthquakes_raw
WHERE tsunami = 1;
""")

show_sql(17, "Tsunami events per year",
"""
SELECT YEAR(FROM_UNIXTIME(time/1000)) AS year, COUNT(*) AS count
FROM earthquakes_raw
WHERE tsunami = 1
GROUP BY year;
""")

show_sql(18, "Earthquakes by alert level",
"""
SELECT alert, COUNT(*) AS count
FROM earthquakes_raw
GROUP BY alert;
""")

show_sql(19, "Average magnitude by alert level",
"""
SELECT alert, AVG(mag) AS avg_magnitude
FROM earthquakes_raw
GROUP BY alert;
""")

show_sql(20, "High-magnitude tsunami events (mag > 7)",
"""
SELECT *
FROM earthquakes_raw
WHERE tsunami = 1 AND mag > 7
LIMIT 15;
""")

# 🔹 Pattern & Risk Analysis
show_sql(21, "Shallow vs Deep earthquake count",
"""
SELECT
CASE
 WHEN depth_km < 70 THEN 'Shallow'
 WHEN depth_km > 300 THEN 'Deep'
 ELSE 'Intermediate'
END AS depth_category,
COUNT(*) AS count
FROM earthquakes_raw
GROUP BY depth_category;
""")

show_sql(22, "15 most recent earthquakes",
"""
SELECT *
FROM earthquakes_raw
ORDER BY time DESC
LIMIT 15;
""")

show_sql(23, "Earthquakes near the equator (±5° latitude)",
"""
SELECT *
FROM earthquakes_raw
WHERE latitude BETWEEN -5 AND 5
LIMIT 15;
""")

show_sql(24, "Deep-focus earthquakes (>300 km)",
"""
SELECT *
FROM earthquakes_raw
WHERE depth_km > 300
LIMIT 15;
""")

show_sql(25, "Average earthquake depth per year",
"""
SELECT YEAR(FROM_UNIXTIME(time/1000)) AS year, AVG(depth_km) AS avg_depth
FROM earthquakes_raw
GROUP BY year;
""")

show_sql(26, "Average earthquake magnitude per year",
"""
SELECT YEAR(FROM_UNIXTIME(time/1000)) AS year, AVG(mag) AS avg_magnitude
FROM earthquakes_raw
GROUP BY year;
""")

show_sql(27, "Weekend vs Weekday earthquake count",
"""
SELECT
CASE
 WHEN DAYOFWEEK(FROM_UNIXTIME(time/1000)) IN (1,7) THEN 'Weekend'
 ELSE 'Weekday'
END AS day_type,
COUNT(*) AS count
FROM earthquakes_raw
GROUP BY day_type;
""")

show_sql(28, "Rounded magnitude distribution",
"""
SELECT ROUND(mag) AS magnitude, COUNT(*) AS count
FROM earthquakes_raw
GROUP BY ROUND(mag)
ORDER BY magnitude;
""")

show_sql(29, "Risk classification based on magnitude",
"""
SELECT
CASE
 WHEN mag >= 7 THEN 'High'
 WHEN mag >= 5 THEN 'Moderate'
 ELSE 'Low'
END AS risk,
COUNT(*) AS count
FROM earthquakes_raw
GROUP BY risk;
""")

show_sql(30, "Events with magnitude error greater than 0.5",
"""
SELECT *
FROM earthquakes_raw
WHERE magError > 0.5
LIMIT 15;
""")

st.success("✅ All 30 SQL questions loaded successfully")