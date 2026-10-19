# Seasonal Tyre Performance Analysis — Issue #72

## Objective

Investigate whether seasonal differences in F1 car performance should affect pit stop predictions.

## Method

- Compare the 2023 and 2024 seasons at Grand Prix events present in both years.
- Reuse the existing pit prediction model's lap cleaning and fuel correction.
- Exclude races with recorded rainfall.
- Match observations by Grand Prix, driver, and tyre compound.
- Require at least three clean laps in each tyre-age group for each season.
- Compare median fuel-corrected lap times for fresh tyres (ages 3–5) and older tyres (ages 12–15).
- Define seasonal change as 2024 tyre slowdown minus 2023 tyre slowdown.

## Results

159 matched driver/tyre comparisons across 14 Grand Prix events.

| Compound | Comparisons | Median seasonal change |
|---|---:|---:|
| HARD | 116 | +0.065 seconds |
| MEDIUM | 39 | -0.095 seconds |
| SOFT | 4 | -0.220 seconds |

Negative values indicate less measured tyre slowdown in 2024. Positive values indicate more slowdown.

## Existing Pit Stop Model

The existing ML/pit_window.py model already fits tyre-wear estimates separately for each race, allowing race-specific performance differences to influence recommendations.

Retrospective backtest results:

| Season | Model mean error | Baseline mean error |
|---|---:|---:|
| 2023 | 7.54 laps | 5.67 laps |
| 2024 | 6.92 laps | 5.98 laps |

The baseline outperformed the existing model in both seasons. Neither evaluation represents a leakage-free live forecasting test because completed-race information is available.

## Limitations

- No dataset identifying actual car upgrades or modification dates is available.
- Seasonal tyre-performance differences cannot be attributed specifically to car modifications.
- Fuel correction relies on assumptions in the existing model.
- Track conditions, temperature, tyre specifications, race strategy, traffic, and other factors may influence comparisons.
- The SOFT compound has only four matched comparisons.
- This analysis is observational, not a causal estimate or an independently validated improvement in pit stop accuracy.

## Decision

Do not apply an arbitrary seasonal multiplier to pit stop predictions.

Retain the existing race-specific tyre-wear estimation and provide this analysis as evidence for evaluating seasonal performance changes. Direct car-modification modeling requires reliable modification data and additional predictive validation.

## Reproduction

Run analysis:

    python -m ML.seasonal_pit_analysis

Run automated tests:

    python -m unittest tests.test_seasonal_pit_analysis -v

## Implementation

- ML/seasonal_pit_analysis.py
- tests/test_seasonal_pit_analysis.py

The existing pit stop prediction algorithm remains unchanged.
