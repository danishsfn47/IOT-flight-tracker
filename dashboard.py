import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
import time

# =========================
# 🌌 CONFIG
# =========================
st.set_page_config(page_title="Airspace Control System", layout="wide")

# =========================
# 🎨 FUTURISTIC CSS
# =========================
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #020617, #0f172a);
    color: white;
}

h1 {
    text-align: center;
    color: #38bdf8;
}

h2, h3 {
    color: #22c55e;
}

[data-testid="stMetric"] {
    background: rgba(255,255,255,0.05);
    border-radius: 20px;
    padding: 20px;
    backdrop-filter: blur(10px);
    box-shadow: 0px 0px 25px rgba(0,255,255,0.2);
    text-align: center;
}

.block-container {
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# =========================
# ✈️ HEADER
# =========================
st.title("✈️ AIRSPACE CONTROL SYSTEM")
st.caption("IoT Aircraft Monitoring • Perak Region")

# =========================
# 🔄 AUTO REFRESH
# =========================
refresh_rate = st.sidebar.slider("Auto Refresh (seconds)", 5, 60, 10)
time.sleep(refresh_rate)

# =========================
# LOAD DATA
# =========================
conn = sqlite3.connect("flights.db")
df = pd.read_sql_query("SELECT * FROM flights", conn)

df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.dropna(subset=['latitude', 'longitude', 'altitude'])

# Filter Perak
df = df[
    (df['latitude'] >= 3.5) & (df['latitude'] <= 6.0) &
    (df['longitude'] >= 100.0) & (df['longitude'] <= 102.5)
]

if df.empty:
    st.warning("No data available yet")
    st.stop()

# =========================
# 🎛️ SIDEBAR FILTER
# =========================
st.sidebar.title("🎛️ Control Panel")

min_time = df['timestamp'].min().to_pydatetime()
max_time = df['timestamp'].max().to_pydatetime()

time_range = st.sidebar.slider("Time Range", min_time, max_time, (min_time, max_time))

df = df[
    (df['timestamp'] >= pd.to_datetime(time_range[0])) &
    (df['timestamp'] <= pd.to_datetime(time_range[1]))
]

# =========================
# 📊 KPI SECTION
# =========================
st.subheader("📡 System Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("📊 Records", len(df))
col2.metric("✈️ Flights", df['icao24'].nunique())
col3.metric("📈 Avg Altitude", f"{int(df['altitude'].mean())} m")
col4.metric("🟢 Status", "ACTIVE")

st.divider()

# =========================
# 🧠 DATABASE INSIGHTS
# =========================
st.subheader("🗄️ Database Insights")

colA, colB, colC = st.columns(3)

colA.metric("Total Records Stored", len(df))
colB.metric("Unique Aircraft", df['icao24'].nunique())

time_span = df['timestamp'].max() - df['timestamp'].min()
colC.metric("Data Duration", str(time_span).split('.')[0])

st.info(f"""
📡 Data Summary:

- First record: {df['timestamp'].min()}
- Latest record: {df['timestamp'].max()}
- Average altitude: {int(df['altitude'].mean())} m
- Peak hour: {df['timestamp'].dt.hour.value_counts().idxmax()}:00
""")

st.divider()

# =========================
# 📊 ANALYTICS
# =========================
st.subheader("📊 Flight Analytics")

col5, col6 = st.columns(2)

df_sample = df.tail(300).copy()
df_sample['altitude_smooth'] = df_sample['altitude'].rolling(10).mean()

fig1, ax1 = plt.subplots()
ax1.plot(df_sample['timestamp'], df_sample['altitude_smooth'])
ax1.set_title("Altitude Trend")

col5.pyplot(fig1)

df['hour'] = df['timestamp'].dt.hour
flights_per_hour = df.groupby('hour').size()

fig2, ax2 = plt.subplots()
flights_per_hour.plot(kind='bar', ax=ax2)
ax2.set_title("Flight Frequency")

col6.pyplot(fig2)

st.divider()

# =========================
# 🗺️ CLEAN MAP
# =========================
st.subheader("🗺️ Perak Airspace Map")

map_df = df.sort_values(by='timestamp').tail(200)

m = folium.Map(location=[4.5, 101], zoom_start=7)

for _, row in map_df.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=3,
        color="#00ffff",
        fill=True,
        fill_opacity=0.6,
        popup=f"{row['callsign']} | Alt: {int(row['altitude'])}"
    ).add_to(m)

st_folium(m, width=1100, height=500)

# =========================
# 📋 DATABASE TABLE VIEW
# =========================
st.subheader("📋 Flight Data Records")

# Sort latest first
table_df = df.sort_values(by='timestamp', ascending=False)

# Limit rows for performance (adjust if needed)
table_df = table_df.head(500)

# Display scrollable table
st.dataframe(
    table_df,
    use_container_width=True,
    height=400
)

st.success("⚡ System Running Smoothly")

