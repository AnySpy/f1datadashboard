#imports
from dataClasses.vehicle import Vehicle

# TODO: Find a better name and location for this file

# ! Find a place to call this every second. This should be called ~20 times per second.
# ! For an even rougher estimate, maybe we just see how much they use per lap and then run with that?
def get_fuel_change(car: Vehicle) -> float:
    """Gets the change in fuel when supplied with the vehicle.  
    Returned amount must be subtracted from the fuel total after the data is returned.

    Args:
        car (Vehicle): A vehicle datatype. Requires an accurate, updated throttle.

    Returns:
        float: The amount of fuel consumed in kg/s
    """
    # ? Formula is modeled after x^2/36.
    # ? Fuel flow regulations cap fuel consumption at 100kg/h or ~0.0278kg/s at 100% throttle.
    fuel_used = pow(car.throttle, 2)/36
    
    return fuel_used

def _main():
    cat = Vehicle(fuel_level=100.00, throttle=0.52)
    fuel_change = get_fuel_change(cat)
    print(cat.fuel_level - fuel_change)
    return 0

if __name__ == '__main__':
    _main()