# Device Log Summarizer

CLI tool that summarizes device telemetry from a CSV file.
First of all you have to fill real data in device telemetry and then you can see the real output.

## Setup

```bash
pip install matplotlib   # only needed for the chart (Section 3)
```

Python 3.9+ is fine; the summarizer itself uses only the standard library.

## Usage

```bash
# Section 1 tests
python -m unittest -v

# Section 2: summarize CSV -> JSON + terminal table
python summarizer.py device_telemetry.csv -o output/summary.json
# optional: --max-avg-temp 80.0

# Section 3: bar chart from the JSON
python plot_temperatures.py output/summary.json -o output/avg_temperature.png
```

## Files

| File | Purpose |
|------|---------|
| `sanitize.py`, `test_sanitize.py` | Section 1: `clean_sensor_readings()` + tests |
| `summarizer.py` | Section 2: read CSV, group by device, filter, export JSON, print table |
| `plot_temperatures.py` | Section 3: matplotlib bar chart |
| `device_telemetry.csv` | Sample input (includes some bad rows on purpose) |
| `output/summary.json`, `output/avg_temperature.png` | Sample outputs |
| `PROMPT_LOG.md` | How AI was used for Section 3 |

## Error handling

- Missing / empty file, missing columns, or no valid rows: clear error message, exit code 1.
- Bad rows (blank device_id, unknown status, non-numeric/empty temperature) are skipped and counted, not fatal.
- Devices are excluded only if the average is strictly above 80.0 (exactly 80.0 is kept).
