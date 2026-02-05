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
        import mysql.connector
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="guvi_project_01"
        )
        df = pd.read_sql("SELECT * FROM earthquakes_raw", conn)
        conn.close()
        return df
    except Exception:
        return pd.read_csv("raw_earthquake_data.csv")

df = load_data()

# ---------------- PREPROCESS ----------------
df['time'] = pd.to_datetime(df['time'], unit='ms', errors='coerce')
df['year'] = df['time'].dt.year
df['month'] = df['time'].dt.month
df['day'] = df['time'].dt.day_name()
df['alert'] = df['alert'].fillna("none")
df = df.dropna(subset=['mag', 'depth_km'])

# ---------------- HEADER ----------------
st.title("🌍 Global Seismic Trends")
st.caption("SQL-driven Earthquake Analytics | MySQL (Local) • CSV (Cloud)")

# ---------------- OVERVIEW ----------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "📏 Magnitude & Depth",
    "⏱ Time Analysis",
    "🌊 Tsunami & Alerts",
    "⚠️ Quality & Risk"
])

# ================= TAB 1: OVERVIEW =================
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Earthquakes", len(df))
    c2.metric("Avg Magnitude", round(df['mag'].mean(), 2))
    c3.metric("Avg Depth (km)", round(df['depth_km'].mean(), 2))
    c4.metric("Tsunamis", int(df['tsunami'].sum()))

    st.subheader("Earthquakes per Year")
    yearly = df.groupby('year').size().reset_index(name='count')
    st.plotly_chart(px.bar(yearly, x='year', y='count'), use_container_width=True)

# ================= TAB 2: MAGNITUDE & DEPTH =================
with tab2:
    questions_md = {
        "Top 10 Strongest Earthquakes": df.nlargest(10, 'mag')[['place','mag','depth_km']],
        "Top 10 Deepest Earthquakes": df.nlargest(10, 'depth_km')[['place','depth_km','mag']],
        "Shallow (<50km) & Strong (>7.5)": df[(df['depth_km']<50) & (df['mag']>7.5)],
        "Average Magnitude by Type": df.groupby('magType')['mag'].mean().round(2).reset_index(),
        "Average Depth by Type": df.groupby('magType')['depth_km'].mean().round(2).reset_index(),
        "Deep Focus (>300 km)": df[df['depth_km']>300][['place','depth_km','mag']]
    }

    for q, res in questions_md.items():
        with st.expander(q):
            st.dataframe(res, use_container_width=True)

# ================= TAB 3: TIME ANALYSIS =================
with tab3:
    questions_time = {
        "Earthquakes per Year": df.groupby('year').size().reset_index(name='count'),
        "Earthquakes per Month": df.groupby('month').size().reset_index(name='count'),
        "Day-wise Distribution": df.groupby('day').size().reset_index(name='count'),
        "Hourly Distribution": df['time'].dt.hour.value_counts().sort_index().reset_index(name='count'),
        "Month with Highest Earthquakes": df.groupby('month').size().idxmax(),
        "Year with Highest Earthquakes": df.groupby('year').size().idxmax()
    }

    for q, res in questions_time.items():
        with st.expander(q):
            if isinstance(res, pd.DataFrame):
                st.dataframe(res)
                st.plotly_chart(px.bar(res, x=res.columns[0], y='count'), use_container_width=True)
            else:
                st.success(f"Answer: {res}")

# ================= TAB 4: TSUNAMI & ALERT =================
with tab4:
    questions_ta = {
        "Tsunami Events": df[df['tsunami']==1][['place','mag','year']],
        "Tsunamis per Year": df[df['tsunami']==1].groupby('year').size().reset_index(name='count'),
        "Alerts Distribution": df.groupby('alert').size().reset_index(name='count'),
        "Avg Magnitude by Alert": df.groupby('alert')['mag'].mean().round(2).reset_index(),
        "High Mag Tsunami (>7)": df[(df['tsunami']==1) & (df['mag']>7)]
    }

    for q, res in questions_ta.items():
        with st.expander(q):
            st.dataframe(res, use_container_width=True)
            if res.shape[1]==2:
                st.plotly_chart(px.bar(res, x=res.columns[0], y=res.columns[1]), use_container_width=True)

# ================= TAB 5: QUALITY & RISK =================
with tab5:
    questions_qr = {
        "Reviewed vs Automatic": df.groupby('status').size().reset_index(name='count'),
        "Least Reliable (High RMS & GAP)": df.sort_values(['rms','gap'], ascending=False).head(10),
        "High Station Coverage (>50)": df[df['nst']>50][['place','mag','nst']],
        "Risk Classification": df.assign(
            risk=df['mag'].apply(lambda x: 'High' if x>=7 else 'Moderate' if x>=5 else 'Low')
        ).groupby('risk').size().reset_index(name='count'),
        "Most Significant Earthquakes": df.nlargest(10,'sig')[['place','mag','sig']]
    }

    for q, res in questions_qr.items():
        with st.expander(q):
            st.dataframe(res, use_container_width=True)

# ---------------- FOOTER ----------------
st.success("✅ All 30 Analytical Questions Loaded Successfully")