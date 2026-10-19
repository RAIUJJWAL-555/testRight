# PROMPT_LOG.md

This log covers how I used an AI assistant for Section 3 (the bar chart of average temperature per device).

## 1. My first prompt

> Write a Python script that reads `summary.json` (made by my `summarizer.py`) and draws a bar chart of the average temperature for each device using matplotlib. The JSON looks like this: `{"devices": [{"device_id": "DEV_A", "total_records": 4, "average_temperature": 48.9, "error_count": 1}, ...]}`. Save the chart as a PNG file.

## 2. What went wrong in the first version

I ran the script and opened the PNG. The chart was drawn, but it had a few problems:

- The x-axis labels were overlapping and could not be read. The AI had used a long label for each bar (device id + "avg temperature" + record count), which was far too long for the space.
- There was no chart title and no x-axis label, and the y-axis just said "Temp" without a unit.
- The text was getting cut off at the edge of the image because there was no `tight_layout()`.
- The bars had no values on them, so I could not read the exact numbers.

## 3. Prompt I used to fix it

> The x-axis labels overlap and I can't read them. Please use only the device_id as the label and rotate it by 45 degrees. Add the title "Average Temperature per Device", an x-label "Device ID" and a y-label "Average Temperature (°C)". Use `tight_layout()` so nothing gets cut off, show the value on top of each bar, and add a dashed line at the 80°C threshold. Also, if the JSON file is missing, show a clear error message instead of a traceback.

## 4. What I checked myself

- I made sure the chart script uses the same keys that my summarizer writes in the JSON (`devices`, `average_temperature`, `max_average_temperature`).
- I switched matplotlib to the `Agg` backend so the script also runs on a machine without a display.
- I ran the final script on my sample data and looked at the PNG (`output/avg_temperature.png`) to confirm the labels, title and values look fine.