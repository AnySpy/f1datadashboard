# ==========================================================================
# GHOST RACER — Database Structure for storing FastF1 API data
# Task: "Create the Structure for the DB to store data from the api"
# ==========================================================================
# Uses SQLite — no server setup needed, works as a single file, perfect
# for this project's scale. This creates the DB schema AND loads sample
# data from the fastf1 API into it, so you can show a working example.
# ==========================================================================

# %% [1] IMPORTS ------------------------------------------------------------
import sqlite3
import fastf1
import pandas as pd
import os

os.makedirs("f1_cache", exist_ok=True)
fastf1.Cache.enable_cache("f1_cache")

DB_PATH = "f1_data.db"


# %% [2] CREATE THE DATABASE SCHEMA ------------------------------------------
def create_schema(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Sessions table — one row per race/session loaded
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
        year INTEGER NOT NULL,
        event_name TEXT NOT NULL,
        session_type TEXT NOT NULL,
        total_laps INTEGER,
        UNIQUE(year, event_name, session_type)
    )
    """)

    # Laps table — one row per lap, linked to a session
    cur.execute("""
    CREATE TABLE IF NOT EXISTS laps (
        lap_id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        driver TEXT,
        team TEXT,
        lap_number INTEGER,
        lap_time_seconds REAL,
        compound TEXT,
        tyre_life INTEGER,
        track_status TEXT,
        is_pit_lap INTEGER,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id)
    )
    """)

    # Weather table — one row per weather sample, linked to a session
    cur.execute("""
    CREATE TABLE IF NOT EXISTS weather (
        weather_id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        air_temp REAL,
        track_temp REAL,
        humidity REAL,
        rainfall INTEGER,
        sample_time TEXT,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id)
    )
    """)

    conn.commit()
    conn.close()
    print(f"Schema created at {db_path}")


# %% [3] LOAD DATA FROM FASTF1 API INTO THE DB -------------------------------
def load_session_into_db(year, event, session_type, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    session = fastf1.get_session(year, event, session_type)
    session.load()

    laps = session.laps.copy()
    weather = session.weather_data.copy()
    total_laps = int(laps["LapNumber"].max())

    # Insert into sessions table (or get existing session_id if already loaded)
    cur.execute("""
        INSERT OR IGNORE INTO sessions (year, event_name, session_type, total_laps)
        VALUES (?, ?, ?, ?)
    """, (year, event, session_type, total_laps))
    conn.commit()

    cur.execute("""
        SELECT session_id FROM sessions
        WHERE year=? AND event_name=? AND session_type=?
    """, (year, event, session_type))
    session_id = cur.fetchone()[0]

    # Insert laps
    for _, row in laps.iterrows():
        lap_time = row["LapTime"].total_seconds() if pd.notna(row["LapTime"]) else None
        is_pit = 1 if (pd.notna(row.get("PitInTime")) or pd.notna(row.get("PitOutTime"))) else 0
        cur.execute("""
            INSERT INTO laps (session_id, driver, team, lap_number, lap_time_seconds,
                               compound, tyre_life, track_status, is_pit_lap)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id, row.get("Driver"), row.get("Team"), row.get("LapNumber"),
            lap_time, row.get("Compound"), row.get("TyreLife"),
            str(row.get("TrackStatus")), is_pit
        ))

    # Insert weather
    for _, row in weather.iterrows():
        cur.execute("""
            INSERT INTO weather (session_id, air_temp, track_temp, humidity, rainfall, sample_time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            session_id, row.get("AirTemp"), row.get("TrackTemp"),
            row.get("Humidity"), int(bool(row.get("Rainfall"))), str(row.get("Time"))
        ))

    conn.commit()
    conn.close()
    print(f"Loaded {len(laps)} laps and {len(weather)} weather samples for {year} {event} {session_type}")


# %% [4] QUICK CHECK — READ DATA BACK OUT ------------------------------------
def _preview_db(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    print("\n--- Sessions ---")
    print(pd.read_sql("SELECT * FROM sessions", conn))
    print("\n--- Sample laps ---")
    print(pd.read_sql("SELECT * FROM laps LIMIT 5", conn))
    print("\n--- Sample weather ---")
    print(pd.read_sql("SELECT * FROM weather LIMIT 5", conn))
    conn.close()


# %% [5] RUN IT ---------------------------------------------------------------
if __name__ == "__main__":
    create_schema()
    load_session_into_db(2023, "Bahrain", "R")
    _preview_db()