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


# Helper/Debug Functions
def _get_event_names(schedule: EventSchedule):
    """Helper function for getting a list of names. Scaffolded to help with frontend

    Args:
        schedule (EventSchedule): The yearly event schedule

    # TODO: Type hint the return properly
    Returns:
        _type_: _description_
    """
    return schedule.get("EventName")


def _main():
    sched = get_schedule_by_year(2026)
    names = _get_event_names(sched)
    print(names)
    return 0


# Obligatory
if __name__ == '__main__':
    _main()