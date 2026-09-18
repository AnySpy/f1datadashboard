# ==========================================================================
# GHOST RACER — Database Structure for storing FastF1 API data
# Task: "Create the Structure for the DB to store data from the api"
# ==========================================================================
# Uses SQLite — no server setup needed, works as a single file, perfect
# for this project's scale. This creates the DB schema AND loads sample
# data from the fastf1 API into it, so you can show a working example.
# ==========================================================================

# ! Problems:
# !     Calls to the database needs to have a unique key to make sure the event is available during a quick lookup.
# !             We could pass the entire EventSchedule to a frontend helper function to not mangle the data while still presenting the EventName to the user?
# !     We need a way to mark whether an event is a future event and we need to update those events with final standings when they hit the API.

# %% [1] IMPORTS ------------------------------------------------------------
import sqlite3
import fastf1
import pandas as pd
import os

from fastf1.events import Session

os.makedirs("f1_cache", exist_ok=True)
fastf1.Cache.enable_cache("f1_cache")

# TODO: Find a permanent location to store the database on the local machine
DB_PATH = "f1_data.db"


# %% [2] CREATE THE DATABASE SCHEMA ------------------------------------------
# ! This MUST be run at startup. We need somewhere to call this that only runs on init of the app/loss of viable database.
def create_schema(db_path: str = DB_PATH) -> None:
    """Defines the database

    Args:
        db_path (str, optional): The file path for the database. Defaults to DB_PATH.
    """
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

    # Drivers table — one row per driver, per session (a driver's team/
    # number can change across a season, so we key on (session_id,
    # driver_code) rather than one global driver_code).
    # driver_code = FastF1's 3-letter code (e.g. "VER") — this is the
    # SAME value already stored in laps.driver, so it works as a join
    # key without changing the laps table.
    cur.execute("""
    CREATE TABLE IF NOT EXISTS drivers (
        session_id INTEGER NOT NULL,
        driver_code TEXT NOT NULL,
        full_name TEXT,
        team TEXT,
        number INTEGER,
        color TEXT,
        PRIMARY KEY (session_id, driver_code),
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

    """
    ____________________________________________________________________________
    |                            track status table                            |
    ____________________________________________________________________________
    |entryID| session ID |time | track safety status code | track surface temp | 
    ____________________________________________________________________________
    |   0   |    1       | 0.00|              0           |        97.2        | example data
    ____________________________________________________________________________

    """
    cur.execute("""
    CREATE TABLE IF NOT EXISTS trackStatus (
        entryID INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL, 
        time TEXT,
        trackTemp REAL,
        trackSafetyStatus INTEGER, 
        trackSurfaceTemp REAL, 
        FOREIGN KEY (session_id) REFERENCES sessions(session_id)
    )
    """)
    conn.commit()
    conn.close()
    print(f"Schema created at {db_path}")


# %% [3] LOAD DATA FROM FASTF1 API INTO THE DB -------------------------------
def load_session_into_db(session: Session, db_path: str = DB_PATH) -> None:
    """Provided a session, will insert the session data into the database

    Args:
        session (Session): A session object from the fastf1 API.
        db_path (str, optional): The file path for the database. Defaults to DB_PATH.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    session.load()

    laps = session.laps.copy()
    weather = session.weather_data.copy()
    results = session.results.copy()  # has driver code, name, team, number, color
    total_laps = int(laps["LapNumber"].max())
    year = session.date.year
    event = session.event.EventName
    # ? Session5 is the race event. Do we care about practices and qualifiers? If so, we need to handle that.
    session_type = session.event.Session5

    # Insert into sessions table (or get existing session_id if already loaded)
    cur.execute(
        """
        INSERT OR IGNORE INTO sessions (year, event_name, session_type, total_laps)
        VALUES (?, ?, ?, ?)
    """,
        (year, event, session_type, total_laps),
    )
    conn.commit()

    cur.execute(
        """
        SELECT session_id FROM sessions
        WHERE year=? AND event_name=? AND session_type=?
    """,
        (year, event, session_type),
    )
    session_id = cur.fetchone()[0]

    # Insert drivers
    for _, row in results.iterrows():
        cur.execute(
            """
            INSERT OR IGNORE INTO drivers (session_id, driver_code, full_name, team, number, color)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                session_id,
                row.get("Abbreviation"),
                row.get("FullName"),
                row.get("TeamName"),
                row.get("DriverNumber"),
                row.get("TeamColor"),
            ),
        )
    conn.commit()

    # Insert laps
    for _, row in laps.iterrows():
        lap_time = row["LapTime"].total_seconds() if pd.notna(row["LapTime"]) else None
        is_pit = (
            1
            if (pd.notna(row.get("PitInTime")) or pd.notna(row.get("PitOutTime")))
            else 0
        )
        cur.execute(
            """
            INSERT INTO laps (session_id, driver, team, lap_number, lap_time_seconds,
                               compound, tyre_life, track_status, is_pit_lap)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                session_id,
                row.get("Driver"),
                row.get("Team"),
                row.get("LapNumber"),
                lap_time,
                row.get("Compound"),
                row.get("TyreLife"),
                str(row.get("TrackStatus")),
                is_pit,
            ),
        )

    # Insert weather
    for _, row in weather.iterrows():
        cur.execute(
            """
            INSERT INTO weather (session_id, air_temp, track_temp, humidity, rainfall, sample_time)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                session_id,
                row.get("AirTemp"),
                row.get("TrackTemp"),
                row.get("Humidity"),
                int(bool(row.get("Rainfall"))),
                str(row.get("Time")),
            ),
        )

    conn.commit()
    conn.close()
    print(
        f"Loaded {len(results)} drivers, {len(laps)} laps, and {len(weather)} "
        f"weather samples for {year} {event} {session_type}"
    )


# %% [4] QUICK CHECK — READ DATA BACK OUT ------------------------------------
def _preview_db(db_path: str = DB_PATH):
    """Helper function to print out the database

    Args:
        db_path (str, optional): The file path for the database. Defaults to DB_PATH.
    """
    conn = sqlite3.connect(db_path)
    print("\n--- Sessions ---")
    print(pd.read_sql("SELECT * FROM sessions", conn))
    print("\n--- Drivers ---")
    print(pd.read_sql("SELECT * FROM drivers", conn))
    print("\n--- Sample laps ---")
    print(pd.read_sql("SELECT * FROM laps LIMIT 5", conn))
    print("\n--- Sample weather ---")
    print(pd.read_sql("SELECT * FROM weather LIMIT 5", conn))
    conn.close()

def _main():
    create_schema()
    session = fastf1.get_session(2023, "Bahrain", "R")
    load_session_into_db(session)
    _preview_db()
    return 0


# %% [5] RUN IT ---------------------------------------------------------------
if __name__ == "__main__":
    _main()
