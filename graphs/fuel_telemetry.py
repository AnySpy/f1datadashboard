
"""Telemetry-based estimated fuel consumption graph.

Uses throttle readings and elapsed time from FastF1 telemetry.

IMPORTANT:
Fuel values are simulated estimates, not measured F1 fuel levels.
The formula is a simplified model and has not been calibrated
against real fuel consumption data.
"""

import sqlite3
from contextlib import closing
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


DB_PATH = Path(__file__).resolve().parents[1] / "f1_data.db"

# Simplified fuel model from the existing project.
MAX_FUEL_FLOW_KG_S = 1.0 / 36.0

# Do not estimate through long gaps in telemetry.
MAX_SAMPLE_GAP_SECONDS = 10.0


def load_driver_telemetry(
    session_id: int,
    driver_code: str,
    db_path=DB_PATH,
) -> pd.DataFrame:
    """Load throttle telemetry for a driver and race session."""

    db_path = Path(db_path)

    if not db_path.is_file():
        raise FileNotFoundError(
            f"Database not found: {db_path}"
        )

    with closing(sqlite3.connect(str(db_path))) as conn:

        table_exists = conn.execute(
            """
            SELECT 1
            FROM sqlite_master
            WHERE type = 'table'
              AND name = 'live_driver_telemetry'
            """
        ).fetchone()

        if not table_exists:
            raise ValueError(
                "Telemetry table is missing. "
                "Dylan's telemetry integration is required."
            )

        telemetry = pd.read_sql_query(
            """
            SELECT session_time, throttle
            FROM live_driver_telemetry
            WHERE session_id = ?
              AND driver_code = ?
            ORDER BY session_time
            """,
            conn,
            params=(session_id, driver_code.upper()),
        )

    if telemetry.empty:
        raise ValueError(
            f"No telemetry available for {driver_code} "
            f"in session {session_id}."
        )

    return telemetry


def estimate_remaining_fuel(
    telemetry: pd.DataFrame,
    initial_fuel_kg: float = 110.0,
) -> pd.DataFrame:
    """Calculate illustrative remaining-fuel estimates."""

    if not 0 < initial_fuel_kg <= 110:
        raise ValueError(
            "Initial fuel must be between 0 and 110 kg."
        )

    required = {"session_time", "throttle"}

    if not required.issubset(telemetry.columns):
        raise ValueError(
            "Missing session_time or throttle column."
        )

    data = telemetry[
        ["session_time", "throttle"]
    ].copy()

    data["session_time"] = pd.to_numeric(
        data["session_time"],
        errors="coerce",
    )

    data["throttle"] = pd.to_numeric(
        data["throttle"],
        errors="coerce",
    )

    if data.isna().any().any():
        raise ValueError(
            "Telemetry contains missing or invalid values."
        )

    if not data["throttle"].between(0, 100).all():
        raise ValueError(
            "Throttle must be between 0 and 100."
        )

    data = (
        data.sort_values("session_time")
        .drop_duplicates("session_time", keep="last")
        .reset_index(drop=True)
    )

    if len(data) < 2:
        raise ValueError(
            "At least two telemetry samples are required."
        )

    # Time difference between telemetry measurements.
    data["delta_time_s"] = (
        data["session_time"].diff().fillna(0.0)
    )

    if (
        data["delta_time_s"] > MAX_SAMPLE_GAP_SECONDS
    ).any():
        raise ValueError(
            "Telemetry gap exceeds 10 seconds. "
            "Cannot estimate across missing data."
        )

    # FastF1 throttle values use 0-100.
    # Our simplified fuel model uses 0-1.
    throttle_fraction = data["throttle"] / 100.0

    # Illustrative fuel flow in kg/second.
    data["fuel_rate_kg_s"] = (
        throttle_fraction ** 2
    ) * MAX_FUEL_FLOW_KG_S

    # Average fuel flow between consecutive samples.
    average_rate = (
        data["fuel_rate_kg_s"]
        + data["fuel_rate_kg_s"].shift(1)
    ) / 2.0

    data["fuel_used_kg"] = (
        average_rate * data["delta_time_s"]
    ).fillna(0.0)

    data["cumulative_fuel_used_kg"] = (
        data["fuel_used_kg"].cumsum()
    )

    data["estimated_remaining_fuel_kg"] = (
        initial_fuel_kg
        - data["cumulative_fuel_used_kg"]
    ).clip(lower=0.0)

    data["elapsed_seconds"] = (
        data["session_time"]
        - data["session_time"].iloc[0]
    )

    return data


def plot_estimated_fuel(
    session_id: int,
    driver_code: str,
    initial_fuel_kg: float = 110.0,
    db_path=DB_PATH,
):
    """Generate a line graph of estimated remaining fuel."""

    telemetry = load_driver_telemetry(
        session_id=session_id,
        driver_code=driver_code,
        db_path=db_path,
    )

    fuel_data = estimate_remaining_fuel(
        telemetry=telemetry,
        initial_fuel_kg=initial_fuel_kg,
    )

    elapsed_minutes = (
        fuel_data["elapsed_seconds"] / 60.0
    )

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(
        elapsed_minutes,
        fuel_data["estimated_remaining_fuel_kg"],
        linewidth=2,
        label=f"{driver_code.upper()} - Estimated Fuel",
    )

    ax.set_title(
        f"Estimated Fuel Remaining - {driver_code.upper()}\n"
        f"Session {session_id} | Simplified throttle model"
    )

    ax.set_xlabel("Elapsed telemetry time (minutes)")
    ax.set_ylabel("Estimated remaining fuel (kg)")

    ax.set_ylim(0, initial_fuel_kg * 1.05)

    ax.grid(True, alpha=0.3)
    ax.legend()

    fig.tight_layout()

    return fig, ax, fuel_data


if __name__ == "__main__":
    print("Fuel telemetry graph module loaded.")
    print(
        "Use plot_estimated_fuel(session_id, driver_code) "
        "when telemetry data is available."
    )
