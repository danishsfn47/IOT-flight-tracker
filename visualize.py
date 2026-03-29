import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import folium

# Connect database
conn = sqlite3.connect("flights.db")
df = pd.read_sql_query("SELECT * FROM flights", conn)

# Convert timestamp
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Clean data
df = df.dropna(subset=['latitude', 'longitude', 'altitude'])
df = df.sort_values(by='timestamp')

# =========================
# 📊 GRAPH 1: Smoothed Altitude Trend
# =========================
df_sample = df.tail(300)  # recent data

# Smooth altitude using rolling average
df_sample['altitude_smooth'] = df_sample['altitude'].rolling(window=10).mean()

plt.figure()
plt.plot(df_sample['timestamp'], df_sample['altitude_smooth'])
plt.xlabel("Time")
plt.ylabel("Altitude")
plt.title("Smoothed Altitude Trend (Realistic)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("altitude_trend.png")
plt.close()

# =========================
# 📊 GRAPH 2: Flights Over Time (15-min bins)
# =========================
df['time_bin'] = df['timestamp'].dt.floor('15min')
flights_time = df.groupby('time_bin').size()

plt.figure()
flights_time.plot()
plt.xlabel("Time")
plt.ylabel("Number of Flights")
plt.title("Flight Activity Over Time")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("flight_activity.png")
plt.close()


# =========================
# 📊 GRAPH 3: Altitude Bands
# =========================
def altitude_band(alt):
    if alt < 5000:
        return "Low (<5k)"
    elif alt < 20000:
        return "Medium (5k-20k)"
    else:
        return "High (>20k)"


df['alt_band'] = df['altitude'].apply(altitude_band)
band_counts = df['alt_band'].value_counts()

plt.figure()
band_counts.plot(kind='bar')
plt.xlabel("Altitude Band")
plt.ylabel("Number of Flights")
plt.title("Flight Altitude Categories")
plt.tight_layout()
plt.savefig("altitude_bands.png")
plt.close()

# =========================
# 🗺️ MAP: PERAK FLIGHTS ONLY (CLEAN)
# =========================
import folium

# Perak center
m = folium.Map(location=[4.5, 101], zoom_start=7)

# Filter strictly Perak (extra safety)
perak_df = df[
    (df['latitude'] >= 3.5) & (df['latitude'] <= 6.0) &
    (df['longitude'] >= 100.0) & (df['longitude'] <= 102.5)
]

# Limit to recent data (avoid clutter)
perak_df = perak_df.tail(150)

# Plot ONLY points (clean)
for _, row in perak_df.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=4,
        popup=f"{row['callsign']} | Alt: {int(row['altitude'])}",
    ).add_to(m)

# Save map
m.save("perak_flights_map.html")

print("✅ Clean Perak map generated!")