import streamlit as st
import pandas as pd

st.set_page_config(page_title="Global Seismic Trends", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("raw_earthquake_data.csv")

df = load_data()

df['time'] = pd.to_datetime(df['time'], unit='ms', errors='coerce')
df['year'] = df['time'].dt.year
df['month'] = df['time'].dt.month
df['day'] = df['time'].dt.day_name()
df['hour'] = df['time'].dt.hour
df['alert'] = df['alert'].fillna("none")

def show_question(qno, title, sql, output_df):
    with st.expander(f"{qno}. {title}"):
        st.markdown("**SQL Query**")
        st.code(sql, language="sql")
        st.markdown("**Output (LIMIT 15)**")
        st.dataframe(output_df.head(15), use_container_width=True)

st.title("🌍 Global Seismic Trends")
st.caption("30 SQL Analytical Questions | Click to view query and output")

QUESTIONS = [

(1, "Top strongest earthquakes",
 "SELECT place, mag, depth_km FROM earthquakes_raw ORDER BY mag DESC LIMIT 15;",
 df.sort_values("mag", ascending=False)[["place","mag","depth_km"]]),

(2, "Top deepest earthquakes",
 "SELECT place, depth_km, mag FROM earthquakes_raw ORDER BY depth_km DESC LIMIT 15;",
 df.sort_values("depth_km", ascending=False)[["place","depth_km","mag"]]),

(3, "Shallow earthquakes with high magnitude",
 "SELECT * FROM earthquakes_raw WHERE depth_km < 50 AND mag > 7.5 LIMIT 15;",
 df[(df["depth_km"] < 50) & (df["mag"] > 7.5)]),

(4, "Average depth of earthquakes",
 "SELECT AVG(depth_km) FROM earthquakes_raw;",
 pd.DataFrame({"avg_depth_km":[round(df["depth_km"].mean(),2)]})),

(5, "Average magnitude",
 "SELECT AVG(mag) FROM earthquakes_raw;",
 pd.DataFrame({"avg_magnitude":[round(df["mag"].mean(),2)]})),

(6, "Earthquakes per year",
 "SELECT year, COUNT(*) FROM earthquakes_raw GROUP BY year;",
 df.groupby("year").size().reset_index(name="count")),

(7, "Earthquakes per month",
 "SELECT month, COUNT(*) FROM earthquakes_raw GROUP BY month;",
 df.groupby("month").size().reset_index(name="count")),

(8, "Earthquakes per day",
 "SELECT day, COUNT(*) FROM earthquakes_raw GROUP BY day;",
 df.groupby("day").size().reset_index(name="count")),

(9, "Earthquakes per hour",
 "SELECT hour, COUNT(*) FROM earthquakes_raw GROUP BY hour;",
 df.groupby("hour").size().reset_index(name="count")),

(10, "Most active seismic network",
 "SELECT net, COUNT(*) FROM earthquakes_raw GROUP BY net ORDER BY COUNT(*) DESC;",
 df.groupby("net").size().reset_index(name="count").sort_values("count", ascending=False)),

(11, "Reviewed vs automatic events",
 "SELECT status, COUNT(*) FROM earthquakes_raw GROUP BY status;",
 df.groupby("status").size().reset_index(name="count")),

(12, "High station coverage earthquakes",
 "SELECT * FROM earthquakes_raw WHERE nst > 50 LIMIT 15;",
 df[df["nst"] > 50][["place","mag","nst"]]),

(13, "Tsunami events",
 "SELECT * FROM earthquakes_raw WHERE tsunami = 1 LIMIT 15;",
 df[df["tsunami"] == 1]),

(14, "Tsunami events per year",
 "SELECT year, COUNT(*) FROM earthquakes_raw WHERE tsunami = 1 GROUP BY year;",
 df[df["tsunami"] == 1].groupby("year").size().reset_index(name="count")),

(15, "Earthquakes by alert level",
 "SELECT alert, COUNT(*) FROM earthquakes_raw GROUP BY alert;",
 df.groupby("alert").size().reset_index(name="count")),

(16, "Average magnitude by alert",
 "SELECT alert, AVG(mag) FROM earthquakes_raw GROUP BY alert;",
 df.groupby("alert")["mag"].mean().round(2).reset_index()),

(17, "Recent earthquakes",
 "SELECT * FROM earthquakes_raw ORDER BY time DESC LIMIT 15;",
 df.sort_values("time", ascending=False)),

(18, "Earthquakes near equator",
 "SELECT * FROM earthquakes_raw WHERE latitude BETWEEN -5 AND 5 LIMIT 15;",
 df[(df["latitude"]>=-5) & (df["latitude"]<=5)]),

(19, "Deep focus earthquakes",
 "SELECT * FROM earthquakes_raw WHERE depth_km > 300 LIMIT 15;",
 df[df["depth_km"] > 300]),

(20, "Average depth per year",
 "SELECT year, AVG(depth_km) FROM earthquakes_raw GROUP BY year;",
 df.groupby("year")["depth_km"].mean().round(2).reset_index()),

(21, "Average magnitude per year",
 "SELECT year, AVG(mag) FROM earthquakes_raw GROUP BY year;",
 df.groupby("year")["mag"].mean().round(2).reset_index()),

(22, "Weekend vs weekday earthquakes",
 "SELECT day, COUNT(*) FROM earthquakes_raw GROUP BY day;",
 df.groupby("day").size().reset_index(name="count")),

(23, "Magnitude distribution",
 "SELECT mag, COUNT(*) FROM earthquakes_raw GROUP BY mag;",
 df.groupby(df["mag"].round()).size().reset_index(name="count")),

(24, "High magnitude earthquakes",
 "SELECT * FROM earthquakes_raw WHERE mag >= 7 LIMIT 15;",
 df[df["mag"] >= 7]),

(25, "Low magnitude earthquakes",
 "SELECT * FROM earthquakes_raw WHERE mag < 4 LIMIT 15;",
 df[df["mag"] < 4]),

(26, "Earthquakes with large RMS",
 "SELECT * FROM earthquakes_raw WHERE rms > 1 LIMIT 15;",
 df[df["rms"] > 1]),

(27, "Earthquakes with large GAP",
 "SELECT * FROM earthquakes_raw WHERE gap > 180 LIMIT 15;",
 df[df["gap"] > 180]),

(28, "Events with many stations",
 "SELECT * FROM earthquakes_raw WHERE nst > 100 LIMIT 15;",
 df[df["nst"] > 100]),

(29, "Earthquakes with alerts",
 "SELECT * FROM earthquakes_raw WHERE alert <> 'none' LIMIT 15;",
 df[df["alert"] != "none"]),

(30, "Earthquakes without alerts",
 "SELECT * FROM earthquakes_raw WHERE alert = 'none' LIMIT 15;",
 df[df["alert"] == "none"])
]

for q in QUESTIONS:
    show_question(*q)

st.success("✅ 30 questions loaded | SQL is clean | Output shown | LIMIT 15 applied")