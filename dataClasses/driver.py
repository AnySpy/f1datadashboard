from vehicle import Vehicle


# ? Is there any other information to add to the driver class?
class Driver:
    # ? Initial variables are intentionally dummy variables
    def __init__(
        self,
        name: str = "ABCXYZ",
        vehicle: Vehicle = Vehicle(),
        current_placement: int = -1,
    ):
        """Constructor for the driver class

        Args:
            name (str, optional): The name of the driver. Defaults to "ABCXYZ".
            vehicle (Vehicle, optional): The vehicle object the driver is operating. Defaults to Vehicle().
            current_placement (int, optional): The current placement of the driver. Defaults to -1.
        """
        self.name = name
        self.vehicle = vehicle
        self.current_placement = current_placement

    def get_name(self) -> str:
        """Getter for the name of the driver.

        Returns:
            str: The name of the driver.
        """
        return self.name

    def set_name(self, name: str) -> None:
        """Setter for the name of the driver.

        Args:
            name (str): The name of the driver.
        """
        self.name = name

    def get_vehicle(self) -> Vehicle:
        """Getter for the vehicle of the driver.

        Returns:
            Vehicle: The vehicle object the driver is operating.
        """
        return self.vehicle

    def set_vehicle(self, vehicle: Vehicle) -> None:
        """Setter for the vehicle of the driver.

        Args:
            vehicle (Vehicle): The vehicle object the driver is operating.
        """
        self.vehicle = vehicle

    def get_current_placement(self) -> int:
        """Getter for the current placement of the driver.

        Returns:
            int: The current placement of the driver.
        """
        return self.current_placement

    def set_current_placement(self, current_placement: int) -> None:
        """Setter for the current placement of the driver.

        Args:
            current_placement (int): The current placement of the driver.
        """
        self.current_placement = current_placement

    name = property(get_name, set_name)
    vehicle = property(get_vehicle, set_vehicle)
    current_placement = property(get_current_placement, set_current_placement)


def _main():
    return 0


if __name__ == "__main__":
    _main()
