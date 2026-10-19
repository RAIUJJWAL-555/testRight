"""Section 1: clean and normalize raw sensor readings."""

import math

MAX_READING = 500.0


def clean_sensor_readings(readings):
    """Return a cleaned list of floats from a list of mixed sensor inputs.

    Rules:
      1. Convert each element to float. Drop it if it is None, cannot be
         converted, is NaN/inf, or is negative (< 0).
      2. Cap any value above 500.0 to 500.0.
      3. An empty list, None, or a list with only invalid entries returns [].
    """
    if not readings:
        return []

    cleaned = []
    for value in readings:
        if value is None or isinstance(value, bool):
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if math.isnan(number) or math.isinf(number) or number < 0:
            continue
        cleaned.append(min(number, MAX_READING))
    return cleaned
