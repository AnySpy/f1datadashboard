import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.lines import Line2D
from graphs.helper_functions import get_fuel_change
from dataClasses.vehicle import Vehicle
from dataClasses.driver import Driver
from numpy import linspace
import random
import typing

# TODO: Fix bug where the graph disappears from a shape mismatch
# TODO: Figure out how this will plug into the frontend

# ? Would a bar graph be better for this? Or do we want a line graph plotted over time?
# ! We may need to precompile the data for graphs? It doesn't seem to function very well while making graphs on-the-fly.
def fuel_graph(driver_list: list[Driver]) -> None:
    """Generates the fuel graph animation

    Args:
        driver_list (list[Driver]): A list of every driver object participating in the race
    """
    # ? Initialization of the matplotlib plot
    fig, ax = plt.subplots(figsize=(16,9))
    # ? We need a list that is 7200 elements long with each element representing time in seconds (elem0 = 0s, elem1 = 1s, etc.)
    time = linspace(0, 7200, 7200)

    # ? Dict{Driver.name, list[float]}
    # ? The idx for the value is the number of seconds that have passed since the start of the simulation.
    # ! We may need to experiment with better data types/storage mechanics since this is storing a float (4 bytes) 20 times every second for the entire race (5400-7200 seconds)
    # !     This would equate to 432,000-576,000 bytes (0.412-0.549 MB) of RAM required per race. Not including other overhead.
    fuel_over_time = {}
    artist_list = []

    _update_fuel_dict(fuel_over_time, driver_list, init=True)

    # ? Iterates over the number of participants in the race and grabs each artist object for animation later.
    for i in range(len(driver_list)):
        line, = ax.plot(fuel_over_time[driver_list[i].name], label=driver_list[i].name)
        artist_list.append(line)

    # ? Generates the data necessary to generate the simulated graph
    for _ in range(7200):
        # ! Remove this when it gets plugged into the API
        _new_throttle(driver_list)
        _update_fuel_dict(fuel_over_time, driver_list)

    ax.set(xlim=(0,7200), ylim=(0, 110), xlabel="Time [s]", ylabel="Fuel [kg]")
    ax.legend()

    # I hate nested functions :(
    def update(frame: int) -> list[Line2D]:
        """The update function for the animation loop

        Args:
            frame (int): Passed by FuncAnimation, represents which frame to render

        Returns:
            list[Line2D]: The list of artist objects that have been updated in this function
        """
        # ? Can be used to speed up playback. 1 is rendering each frame, 10 is rendering every 10 frames.
        frame = frame * 15
        for i in range(len(artist_list)):
            line = artist_list[i]
            fuel_list = fuel_over_time[driver_list[i].name][:frame]
            t = time[:frame]
            line.set_xdata(t)
            line.set_ydata(fuel_list)
        return artist_list

    # ? Renders and shows the full animation
    ani = animation.FuncAnimation(fig=fig, func=update, frames=len(fuel_over_time[driver_list[0].name]), interval=10)
    plt.show()

# TODO: Hook into the API handler to get raw data
def _update_fuel_dict(fuel_dict: typing.Dict[str, list[float]], driver_list: list[Driver], init: bool = False) -> typing.Dict[str, list[float]]:
    """Updates the fuel dictionary, initializing the dictionary when `init = True` and appending new values when `init = False`

    Args:
        fuel_dict (typing.Dict[str, list[float]]): A dictionary the contains the driver's name as the key and a list where the index represents time and the value represents remaining fuel.
        driver_list (list[Driver]): A list that contains the driver objects participating in the race.
        init (bool, optional): Whether this is the initialization of the fuel dictionary. Defaults to False.

    Returns:
        typing.Dict[str, list[float]]: _description_
    """
    # ? Initializes the dictionary to have the names of drivers as the key and 110kg of fuel at time=0
    if init:
        for i in range(len(driver_list)):
            fuel_dict[driver_list[i].name] = [driver_list[i].vehicle.fuel_level]
        return fuel_dict
    
    for i in range(len(driver_list)):
        # ? Obtains the fuel used over the last second given the throttle applied currently
        fuel_used = get_fuel_change(driver_list[i].vehicle)
        # ? Updates the fuel the driver has left
        driver_list[i].vehicle.fuel_level -= fuel_used
        # ? If the fuel remaining is below 0, that's impossible so we set it to 0
        if driver_list[i].vehicle.fuel_level - fuel_used < 0:
            driver_list[i].vehicle.fuel_level = 0
        # ? Appends each new fuel entry to the respective driver
        fuel_dict[driver_list[i].name].append(driver_list[i].vehicle.fuel_level)
    return fuel_dict

def _new_throttle(driver_list: list[Driver]) -> None:
    """Generates a **RANDOM** new throttle for the driver. For simulation purposes ONLY!!!

    Args:
        driver_list (list[Driver]): The list of driver objects participating in the race
    """
    for i in range(len(driver_list)):
        driver_list[i].vehicle.throttle = random.uniform(0.00, 1.00)

def _main():
    # ? Seed can be removed, this is just for testing purposes :)
    random.seed(220082)
    driver_list = []
    for i in range(20):
        # ! Throttle is set randomly. This needs to be removed eventually and replaced with API calls.
        _vehicle = Vehicle(fuel_level=110, throttle=random.uniform(0.00, 1.00))
        _driver = Driver(name=f"DRV{i}", vehicle=_vehicle)
        driver_list.append(_driver)

    fuel_graph(driver_list)

    return 0

if __name__ == '__main__':
    _main()