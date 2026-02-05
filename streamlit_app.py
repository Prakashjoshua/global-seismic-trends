import streamlit as st
import pandas as pd
import plotly.express as px

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Global Seismic Trends", layout="wide")

# ================= LOAD DATA =================
@st.cache_data
def load_data():
    return pd.read_csv("raw_earthquake_data.csv")

df = load_data()

# ================= PREPROCESS =================
df['time'] = pd.to_datetime(df['time'], unit='ms', errors='coerce')
df['year'] = df['time'].dt.year
df['month'] = df['time'].dt.month
df['day'] = df['time'].dt.day_name()
df['hour'] = df['time'].dt.hour
df['alert'] = df['alert'].fillna("none")
df = df.dropna(subset=['mag', 'depth_km'])

# ================= HELPER =================
def render_question(qno, title, sql, df_out, chart=None):
    with st.expander(f"{qno}. {title}"):
        st.markdown("**SQL Query**")
        st.code(sql, language="sql")
        st.markdown("**Output**")
        st.dataframe(df_out, use_container_width=True)
        if chart is not None:
            st.plotly_chart(chart, use_container_width=True, key=f"chart_{qno}")

# ================= HEADER =================
st.title("🌍 Global Seismic Trends")
st.caption("All 30 SQL-style questions with outputs (Cloud-safe)")

# ================= ALL 30 QUESTIONS =================
QUESTIONS = [

# ---------- OVERVIEW ----------
(1, "Earthquakes per Year",
 "SELECT year, COUNT(*) FROM earthquakes_raw GROUP BY year;",
 df.groupby('year').size().reset_index(name='count'),
 px.bar(df.groupby('year').size().reset_index(name='count'), x='year', y='count')),

(2, "Earthquakes per Month",
 "SELECT month, COUNT(*) FROM earthquakes_raw GROUP BY month;",
 df.groupby('month').size().reset_index(name='count'), None),

(3, "Day-wise Distribution",
 "SELECT day, COUNT(*) FROM earthquakes_raw GROUP BY day;",
 df.groupby('day').size().reset_index(name='count'), None),

(4, "Total Tsunami Events",
 "SELECT COUNT(*) FROM earthquakes_raw WHERE tsunami = 1;",
 pd.DataFrame({"tsunami_events": [int(df['tsunami'].sum())]}), None),

(5, "Average Magnitude",
 "SELECT AVG(mag) FROM earthquakes_raw;",
 pd.DataFrame({"avg_magnitude": [round(df['mag'].mean(), 2)]}), None),

# ---------- MAGNITUDE & DEPTH ----------
(6, "Top 10 Strongest Earthquakes",
 "SELECT place, mag FROM earthquakes_raw ORDER BY mag DESC LIMIT 10;",
 df.nlargest(10, 'mag')[['place','mag','depth_km']], None),

(7, "Top 10 Deepest Earthquakes",
 "SELECT place, depth_km FROM earthquakes_raw ORDER BY depth_km DESC LIMIT 10;",
 df.nlargest(10, 'depth_km')[['place','depth_km','mag']], None),

(8, "Shallow & Strong Earthquakes",
 "SELECT * FROM earthquakes_raw WHERE depth_km < 50 AND mag > 7.5;",
 df[(df['depth_km'] < 50) & (df['mag'] > 7.5)], None),

(9, "Average Magnitude by Type",
 "SELECT magType, AVG(mag) FROM earthquakes_raw GROUP BY magType;",
 df.groupby('magType')['mag'].mean().round(2).reset_index(), None),

(10, "Average Depth by Type",
 "SELECT magType, AVG(depth_km) FROM earthquakes_raw GROUP BY magType;",
 df.groupby('magType')['depth_km'].mean().round(2).reset_index(), None),

(11, "Deep Focus Earthquakes (>300km)",
 "SELECT * FROM earthquakes_raw WHERE depth_km > 300;",
 df[df['depth_km'] > 300], None),

(12, "Shallow vs Deep Count",
 "SELECT depth_category, COUNT(*) FROM earthquakes_raw GROUP BY depth_category;",
 pd.DataFrame({
     "category": ["Shallow", "Deep"],
     "count": [(df['depth_km'] < 70).sum(), (df['depth_km'] > 300).sum()]
 }), None),

# ---------- TIME ANALYSIS ----------
(13, "Earthquakes per Hour",
 "SELECT HOUR(time), COUNT(*) FROM earthquakes_raw GROUP BY hour;",
 df.groupby('hour').size().reset_index(name='count'),
 px.bar(df.groupby('hour').size().reset_index(name='count'), x='hour', y='count')),

(14, "Month with Most Earthquakes",
 "SELECT month FROM earthquakes_raw GROUP BY month ORDER BY COUNT(*) DESC LIMIT 1;",
 pd.DataFrame({"month": [df.groupby('month').size().idxmax()]}), None),

(15, "Year with Most Earthquakes",
 "SELECT year FROM earthquakes_raw GROUP BY year ORDER BY COUNT(*) DESC LIMIT 1;",
 pd.DataFrame({"year": [df.groupby('year').size().idxmax()]}), None),

(16, "Weekend vs Weekday",
 "SELECT day_type, COUNT(*) FROM earthquakes_raw GROUP BY day_type;",
 pd.DataFrame({
     "type": ["Weekend", "Weekday"],
     "count": [
         df[df['day'].isin(['Saturday','Sunday'])].shape[0],
         df[~df['day'].isin(['Saturday','Sunday'])].shape[0]
     ]
 }), None),

(17, "Monthly Trend (Year–Month)",
 "SELECT year, month, COUNT(*) FROM earthquakes_raw GROUP BY year, month;",
 df.groupby(['year','month']).size().reset_index(name='count'), None),

(18, "10 Most Recent Earthquakes",
 "SELECT * FROM earthquakes_raw ORDER BY time DESC LIMIT 10;",
 df.sort_values('time', ascending=False).head(10), None),

# ---------- TSUNAMI & ALERTS ----------
(19, "All Tsunami Events",
 "SELECT place, mag FROM earthquakes_raw WHERE tsunami = 1;",
 df[df['tsunami'] == 1][['place','mag','year']], None),

(20, "Tsunamis per Year",
 "SELECT year, COUNT(*) FROM earthquakes_raw WHERE tsunami = 1 GROUP BY year;",
 df[df['tsunami']==1].groupby('year').size().reset_index(name='count'), None),

(21, "Alert Distribution",
 "SELECT alert, COUNT(*) FROM earthquakes_raw GROUP BY alert;",
 df.groupby('alert').size().reset_index(name='count'), None),

(22, "Avg Magnitude by Alert",
 "SELECT alert, AVG(mag) FROM earthquakes_raw GROUP BY alert;",
 df.groupby('alert')['mag'].mean().round(2).reset_index(), None),

(23, "High Magnitude Tsunami Events",
 "SELECT * FROM earthquakes_raw WHERE tsunami=1 AND mag>7;",
 df[(df['tsunami']==1) & (df['mag']>7)], None),

(24, "Percentage of Events with Alerts",
 "SELECT (alerts/total)*100 FROM earthquakes_raw;",
 pd.DataFrame({
     "alert_percentage": [
         round((df[df['alert'] != 'none'].shape[0] / df.shape[0]) * 100, 2)
     ]
 }), None),

# ---------- QUALITY & RISK ----------
(25, "Reviewed vs Automatic",
 "SELECT status, COUNT(*) FROM earthquakes_raw GROUP BY status;",
 df.groupby('status').size().reset_index(name='count'), None),

(26, "Top 10 Most Significant Earthquakes",
 "SELECT place, sig FROM earthquakes_raw ORDER BY sig DESC LIMIT 10;",
 df.nlargest(10, 'sig')[['place','mag','sig']], None),

(27, "High Station Coverage (>50)",
 "SELECT * FROM earthquakes_raw WHERE nst > 50;",
 df[df['nst'] > 50][['place','mag','nst']], None),

(28, "Least Reliable (High RMS & GAP)",
 "SELECT * FROM earthquakes_raw ORDER BY rms DESC, gap DESC LIMIT 10;",
 df.sort_values(['rms','gap'], ascending=False).head(10), None),

(29, "Risk Classification",
 """
 SELECT CASE
  WHEN mag >= 7 THEN 'High'
  WHEN mag >= 5 THEN 'Moderate'
  ELSE 'Low'
 END AS risk, COUNT(*)
 FROM earthquakes_raw GROUP BY risk;
 """,
 df.assign(
     risk=df['mag'].apply(lambda x: 'High' if x>=7 else 'Moderate' if x>=5 else 'Low')
 ).groupby('risk').size().reset_index(name='count'), None),

(30, "Earthquakes Near Equator (±5°)",
 "SELECT * FROM earthquakes_raw WHERE latitude BETWEEN -5 AND 5;",
 df[(df['latitude'] >= -5) & (df['latitude'] <= 5)], None),
]

# ================= RENDER =================
for q in QUESTIONS:
    render_question(*q)

st.success("✅ All 30 questions are now visible with SQL + Output")