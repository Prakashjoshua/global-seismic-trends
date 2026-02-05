import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Global Seismic Trends",
    layout="wide"
)

# ---------------- LOAD DATA (CSV ONLY – CLOUD SAFE) ----------------
@st.cache_data
def load_data():
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
st.caption("Earthquake Analytics Dashboard (30 Queries | Cloud Safe)")

# ---------------- TABS ----------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "📏 Magnitude & Depth",
    "⏱ Time Analysis",
    "🌊 Tsunami & Alerts",
    "⚠️ Quality & Risk"
])

# =====================================================
# TAB 1: OVERVIEW (Queries 1–5)
# =====================================================
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Earthquakes", len(df))
    c2.metric("Avg Magnitude", round(df['mag'].mean(), 2))
    c3.metric("Avg Depth (km)", round(df['depth_km'].mean(), 2))
    c4.metric("Tsunamis", int(df['tsunami'].sum()))

    with st.expander("1️⃣ Earthquakes per Year"):
        res = df.groupby('year').size().reset_index(name='count')
        st.dataframe(res)
        st.plotly_chart(px.bar(res, x='year', y='count'),
                        use_container_width=True,
                        key="q1")

    with st.expander("2️⃣ Earthquakes per Month"):
        res = df.groupby('month').size().reset_index(name='count')
        st.dataframe(res)
        st.plotly_chart(px.bar(res, x='month', y='count'),
                        use_container_width=True,
                        key="q2")

    with st.expander("3️⃣ Day-wise Earthquake Count"):
        res = df.groupby('day').size().reset_index(name='count')
        st.dataframe(res)

    with st.expander("4️⃣ Total Tsunami Events"):
        st.success(df['tsunami'].sum())

    with st.expander("5️⃣ Average Magnitude"):
        st.success(round(df['mag'].mean(), 2))

# =====================================================
# TAB 2: MAGNITUDE & DEPTH (Queries 6–12)
# =====================================================
with tab2:
    with st.expander("6️⃣ Top 10 Strongest Earthquakes"):
        st.dataframe(df.nlargest(10, 'mag')[['place','mag','depth_km']])

    with st.expander("7️⃣ Top 10 Deepest Earthquakes"):
        st.dataframe(df.nlargest(10, 'depth_km')[['place','depth_km','mag']])

    with st.expander("8️⃣ Shallow (<50 km) & Strong (>7.5)"):
        st.dataframe(df[(df['depth_km']<50) & (df['mag']>7.5)])

    with st.expander("9️⃣ Average Magnitude by Type"):
        res = df.groupby('magType')['mag'].mean().round(2).reset_index()
        st.dataframe(res)

    with st.expander("🔟 Average Depth by Type"):
        res = df.groupby('magType')['depth_km'].mean().round(2).reset_index()
        st.dataframe(res)

    with st.expander("1️⃣1️⃣ Deep Focus Earthquakes (>300 km)"):
        st.dataframe(df[df['depth_km'] > 300])

    with st.expander("1️⃣2️⃣ Shallow vs Deep Count"):
        shallow = len(df[df['depth_km'] < 70])
        deep = len(df[df['depth_km'] > 300])
        st.write({"Shallow": shallow, "Deep": deep})

# =====================================================
# TAB 3: TIME ANALYSIS (Queries 13–18)
# =====================================================
with tab3:
    with st.expander("1️⃣3️⃣ Earthquakes per Hour"):
        res = df['time'].dt.hour.value_counts().sort_index().reset_index(name='count')
        st.dataframe(res)
        st.plotly_chart(px.bar(res, x='index', y='count'),
                        use_container_width=True,
                        key="q13")

    with st.expander("1️⃣4️⃣ Month with Highest Earthquakes"):
        st.success(df.groupby('month').size().idxmax())

    with st.expander("1️⃣5️⃣ Year with Highest Earthquakes"):
        st.success(df.groupby('year').size().idxmax())

    with st.expander("1️⃣6️⃣ Weekend vs Weekday Count"):
        weekend = df[df['day'].isin(['Saturday','Sunday'])].shape[0]
        weekday = df.shape[0] - weekend
        st.write({"Weekend": weekend, "Weekday": weekday})

    with st.expander("1️⃣7️⃣ Monthly Trend"):
        res = df.groupby(['year','month']).size().reset_index(name='count')
        st.dataframe(res)

    with st.expander("1️⃣8️⃣ Recent 10 Earthquakes"):
        st.dataframe(df.sort_values('time', ascending=False).head(10))

# =====================================================
# TAB 4: TSUNAMI & ALERTS (Queries 19–24)
# =====================================================
with tab4:
    with st.expander("1️⃣9️⃣ Tsunami Events"):
        st.dataframe(df[df['tsunami']==1][['place','mag','year']])

    with st.expander("2️⃣0️⃣ Tsunamis per Year"):
        res = df[df['tsunami']==1].groupby('year').size().reset_index(name='count')
        st.dataframe(res)

    with st.expander("2️⃣1️⃣ Alert Distribution"):
        res = df.groupby('alert').size().reset_index(name='count')
        st.dataframe(res)

    with st.expander("2️⃣2️⃣ Avg Magnitude by Alert"):
        res = df.groupby('alert')['mag'].mean().round(2).reset_index()
        st.dataframe(res)

    with st.expander("2️⃣3️⃣ High Magnitude Tsunami (>7)"):
        st.dataframe(df[(df['tsunami']==1) & (df['mag']>7)])

    with st.expander("2️⃣4️⃣ % of Events with Alerts"):
        percent = (df[df['alert']!='none'].shape[0]/df.shape[0])*100
        st.success(f"{round(percent,2)}%")

# =====================================================
# TAB 5: QUALITY & RISK (Queries 25–30)
# =====================================================
with tab5:
    with st.expander("2️⃣5️⃣ Reviewed vs Automatic"):
        st.dataframe(df.groupby('status').size().reset_index(name='count'))

    with st.expander("2️⃣6️⃣ Most Significant Earthquakes"):
        st.dataframe(df.nlargest(10,'sig')[['place','mag','sig']])

    with st.expander("2️⃣7️⃣ High Station Coverage (>50)"):
        st.dataframe(df[df['nst']>50][['place','mag','nst']])

    with st.expander("2️⃣8️⃣ Least Reliable (High RMS & GAP)"):
        st.dataframe(df.sort_values(['rms','gap'], ascending=False).head(10))

    with st.expander("2️⃣9️⃣ Risk Classification"):
        res = df.assign(
            risk=df['mag'].apply(
                lambda x: 'High' if x>=7 else 'Moderate' if x>=5 else 'Low'
            )
        ).groupby('risk').size().reset_index(name='count')
        st.dataframe(res)

    with st.expander("3️⃣0️⃣ Earthquakes Near Equator (±5°)"):
        st.dataframe(df[(df['latitude']>=-5) & (df['latitude']<=5)])

# ---------------- FOOTER ----------------
st.success("✅ 30 Analytical Questions Loaded Successfully (Stable Version)")