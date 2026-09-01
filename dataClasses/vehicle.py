from typing import Any


class Vehicle:
    # ? Initial variables are intentionally dummy variables
    def __init__(
        self,
        coordinates: list[float] = [0.00, 0.00, 0.00],
        curr_fuel_level: float = -100.00,
        curr_throttle: float = -1.00,
        curr_brake: float = -1.00,
        curr_gear: Any = -1,
    ):
        """Constructor for the vehicle class

        Args:
            coordinates (list[float], optional): A list containing coordinates in the format of [x, y, z]. Defaults to [0.00, 0.00, 0.00].
            fuel_level (float, optional): A float representing the percentage of fuel left. Defaults to -100.00.
            throttle (float, optional): A float representing the percentage of throttle applied. Defaults to -1.00.
            brake (float, optional): A float representing the percentage of brake applied. Defaults to -1.00.
            gear (Any, optional): The gear of the vehicle. Defaults to -1.
        """
        # ? Should coordinates be passed in a list/tuple, or do we want each coord passed individually?
        self.x = coordinates[0]
        self.y = coordinates[1]
        self.z = coordinates[2]
        self.fuel_level = curr_fuel_level
        self.throttle = curr_throttle
        self.brake = curr_brake
        # ? What is gear in this context?
        self.gear = curr_gear

    def get_coords(self) -> list[float]:
        """Getter for the coordinates

        Returns:
            list[float]: A list containing coordinates in the format of [x, y, z]
        """
        return [self.x, self.y, self.z]

    def set_coords(self, coordinates: list[float]) -> None:
        """Setter for the coordinates

        Args:
            coordinates (list[float]): A list containing coordinates in the format of [x, y, z]
        """
        self.x = coordinates[0]
        self.y = coordinates[1]
        self.z = coordinates[2]

    def get_fuel_level(self) -> float:
        """Getter for the fuel level

        Returns:
            float: A float representing the percentage of fuel left.
        """
        return self.fuel_level

    def set_fuel_level(self, curr_fuel_level: float) -> None:
        """Setter for the fuel level

        Args:
            fuel_level (float): A float representing the percentage of fuel left
        """
        self.fuel_level = curr_fuel_level

    def get_throttle(self) -> float:
        """Getter for the throttle applied

        Returns:
            float: A float representing the percentage of throttle applied.
        """
        return self.throttle

    def set_throttle(self, curr_throttle: float) -> None:
        """Setter for the throttle applied

        Args:
            throttle (float): A float representing the percentage of throttle applied.
        """
        self.throttle = curr_throttle

    def get_brake(self) -> float:
        """Getter for the brake applied

        Returns:
            float: A float representing the percentage of brake applied.
        """
        return self.brake

    def set_brake(self, curr_brake: float) -> None:
        """Setter for the brake applied

        Args:
            brake (float): A float representing the percentage of brake applied.
        """
        self.brake = curr_brake

    def get_gear(self) -> Any:
        """Getter for the gear of the vehicle

        Returns:
            Any: The gear of the vehicle.
        """
        return self.gear

    def set_gear(self, curr_gear: Any) -> None:
        """Setter for the gear of the vehicle

        Args:
            gear (Any): The gear of the vehicle.
        """
        self.gear = curr_gear

    coords = property(get_coords, set_coords)
    fuel_level = property(get_fuel_level, set_fuel_level)
    throttle = property(get_throttle, set_throttle)
    brake = property(get_brake, set_brake)
    gear = property(get_gear, set_gear)


def _main():
    return 0


if __name__ == "__main__":
    _main()
