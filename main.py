import sqlite3
import time
import random
from datetime import datetime

conn = sqlite3.connect("flights.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS flights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    icao24 TEXT,
    callsign TEXT,
    latitude REAL,
    longitude REAL,
    altitude REAL,
    timestamp TEXT
)
""")

conn.commit()

def generate_fake_data():
    flights = []

    for i in range(10):  # 10 flights each cycle
        icao24 = f"FL{i}{random.randint(100,999)}"
        callsign = f"AK{random.randint(100,999)}"

        # Perak area
        latitude = random.uniform(3.5, 6.0)
        longitude = random.uniform(100.0, 102.5)
        altitude = random.uniform(1000, 40000)

        flights.append((icao24, callsign, latitude, longitude, altitude))

    return flights

def save_data(flights):
    for flight in flights:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        INSERT INTO flights (icao24, callsign, latitude, longitude, altitude, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (*flight, timestamp))

    conn.commit()

while True:
    print("Generating data...")
    flights = generate_fake_data()
    save_data(flights)
    print("Data saved!")

    time.sleep(60)