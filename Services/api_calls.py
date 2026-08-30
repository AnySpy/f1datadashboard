# ----------------------------------------
# This file is meant to handle all API calls, which will then be passed to the database as needed.
# By: Gwyn Young
# ----------------------------------------

# ! Problems:
# !     Calls to the database needs to have a unique key to make sure the event is available.
# !             We could pass the entire EventSchedule to a frontend helper function to not mangle the data while still presenting the EventName to the user?
# !     We need a way to mark whether an event is a future event and we need to update those events with final standings when they hit the API.

# Imports
import fastf1
import database as db
import pandas as pd
from fastf1.events import EventSchedule
import typing


def get_schedule_by_year(year: int, testing: bool = False) -> EventSchedule:
    """When passed a year as an int, will return the name of the events. 
    Should be called to gain a list of events in a year

    Args:
        year (int): Year to grab the event schedule for
        testing (bool): Whether to include testing

    Returns:
        EventSchedule: The full event schedule of the year
    """
    yearlySchedule = fastf1.get_event_schedule(year, include_testing=False)
    return yearlySchedule
    # Names will need to be pushed to frontend for selection.

def get_race(year: int, event_name: str, type: str = "R"):
    """Will get a race from fastf1's API AND load it into the database

    Args:
        year (int): The year the event took place
        event_name (str): The name of the event
        type (str, optional): What type of race to grab. Types: 'FP1', 'FP2', 'FP3', 'Q', 'R'. Defaults to "R".
    """
    db.load_session_into_db(fastf1.get_session(year, event_name, type))


# Helper/Debug Functions
def _get_event_names(schedule: EventSchedule) -> pd.Series[typing.Any] | None:
    """Helper function for getting a list of names. Scaffolded to help with frontend

    Args:
        schedule (EventSchedule): The yearly event schedule

    # TODO: Type hint the return properly (Helper so not priority)
    Returns:
        _type_: _description_
    """
    return schedule.get("EventName")


def _main():
    db.create_schema()
    get_race(2026, "Japanese Grand Prix", "R")
    db._preview_db()
    return 0


# Obligatory
if __name__ == '__main__':
    _main()