# Fuel Consumption Graph - Issue #53

## Objective
Create a graph showing estimated remaining fuel using driver throttle telemetry.

## Implementation
- Added graphs/fuel_telemetry.py.
- Designed to read Dylan's live_driver_telemetry database table.
- Uses session_id and driver_code to select telemetry.
- Converts throttle readings from 0-100 to 0-1.
- Accounts for elapsed time between telemetry samples.
- Calculates illustrative remaining fuel in kilograms.
- Rejects missing data, invalid throttle, and telemetry gaps over 10 seconds.
- Generates a Matplotlib line graph.

## Fuel Estimation
Fuel flow (kg/s) = (throttle / 100)^2 / 36

Fuel used between samples is calculated using average fuel flow multiplied by elapsed time.

Initial fuel defaults to 110 kg and is an assumption.

IMPORTANT: This formula is a simplified simulation model, not a calibrated measurement of real F1 fuel consumption.

## Testing
Eight automated tests passed, including:
- Full and zero throttle
- Variable time intervals
- Invalid throttle readings
- Missing data
- Long telemetry gaps
- Nonnegative remaining fuel
- Graph generation

The graph was also visually checked using controlled sample data.

Run tests:
    python -m unittest tests.test_fuel_telemetry -v

## Limitations
- Real telemetry records are not yet available in the local database.
- The telemetry table is currently defined in the developHome branch.
- The graph is not yet integrated into the application's UI.
- The existing graphs/fuel_consumption.py remains unchanged.
- Actual fuel consumption and starting fuel levels are not available from FastF1.
- Results must be described as illustrative estimates, not measured fuel values.

## Next Steps
- Integrate with populated telemetry once available.
- Test using real race throttle records.
- Connect the graph to the application's graph-selection UI.
- Calibrate the model if reliable fuel-consumption data becomes available.
