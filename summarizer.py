"""Section 2: Device Log Summarizer CLI.

Reads a device telemetry CSV, aggregates per device, drops devices whose
average temperature is above the threshold, writes JSON and prints a table.

Usage:
    python summarizer.py device_telemetry.csv -o output/summary.json
"""

import argparse
import csv
import json
import math
import os
import sys
from collections import defaultdict

REQUIRED_COLUMNS = {"device_id", "status", "temperature"}
VALID_STATUSES = {"ACTIVE", "WARNING", "ERROR"}
DEFAULT_MAX_AVG_TEMP = 80.0


def read_records(csv_path):
    """Read the CSV and return (valid_rows, skipped_rows).

    Each valid row is a (device_id, status, temperature) tuple. Rows with a
    missing device_id, unknown status or non-numeric temperature are skipped
    and counted instead of crashing the program.
    """
    records = []
    skipped = 0

    with open(csv_path, newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError("CSV file is empty.")

        header = {name.strip() for name in reader.fieldnames if name}
        missing = REQUIRED_COLUMNS - header
        if missing:
            raise ValueError(f"CSV is missing required column(s): {', '.join(sorted(missing))}")

        for row in reader:
            device_id = (row.get("device_id") or "").strip()
            status = (row.get("status") or "").strip().upper()
            raw_temp = (row.get("temperature") or "").strip()

            if not device_id or status not in VALID_STATUSES:
                skipped += 1
                continue
            try:
                temperature = float(raw_temp)
            except ValueError:
                skipped += 1
                continue
            if math.isnan(temperature) or math.isinf(temperature):
                skipped += 1
                continue

            records.append((device_id, status, temperature))

    return records, skipped


def aggregate(records):
    """Group records by device_id and compute count, mean temp and error count."""
    temps = defaultdict(list)
    error_counts = defaultdict(int)

    for device_id, status, temperature in records:
        temps[device_id].append(temperature)
        if status == "ERROR":
            error_counts[device_id] += 1

    results = []
    for device_id in sorted(temps):
        readings = temps[device_id]
        results.append(
            {
                "device_id": device_id,
                "total_records": len(readings),
                "average_temperature": sum(readings) / len(readings),
                "error_count": error_counts[device_id],
            }
        )
    return results


def filter_by_avg_temp(devices, max_avg_temp):
    """Split devices into (kept, excluded) based on the average temperature."""
    kept = [d for d in devices if d["average_temperature"] <= max_avg_temp]
    excluded = [d["device_id"] for d in devices if d["average_temperature"] > max_avg_temp]
    return kept, excluded


def save_json(path, devices, excluded, skipped_rows, max_avg_temp):
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)

    rounded_devices = [{**d, "average_temperature": round(d["average_temperature"], 2)} for d in devices]
    payload = {
        "max_average_temperature": max_avg_temp,
        "devices": rounded_devices,
        "excluded_devices": excluded,
        "skipped_rows": skipped_rows,
    }
    with open(path, "w", encoding="utf-8") as json_file:
        json.dump(payload, json_file, indent=2)
        json_file.write("\n")


def print_table(devices):
    headers = ("Device", "Records", "Avg Temp", "Errors")
    rows = [
        (d["device_id"], str(d["total_records"]), f"{d['average_temperature']:.2f}", str(d["error_count"]))
        for d in devices
    ]
    widths = [max(len(h), *(len(r[i]) for r in rows)) if rows else len(h) for i, h in enumerate(headers)]

    def line(cells):
        return " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(cells))

    print(line(headers))
    print("-+-".join("-" * w for w in widths))
    for row in rows:
        print(line(row))


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Summarize device telemetry from a CSV file.")
    parser.add_argument("csv_path", help="Path to device_telemetry.csv")
    parser.add_argument("-o", "--output", default="output/summary.json", help="Output JSON path (default: output/summary.json)")
    parser.add_argument(
        "--max-avg-temp",
        type=float,
        default=DEFAULT_MAX_AVG_TEMP,
        help=f"Exclude devices with an average temperature above this value (default: {DEFAULT_MAX_AVG_TEMP})",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    try:
        records, skipped = read_records(args.csv_path)
    except FileNotFoundError:
        print(f"Error: file not found: {args.csv_path}", file=sys.stderr)
        return 1
    except (ValueError, UnicodeDecodeError, csv.Error, OSError) as error:
        print(f"Error: could not read {args.csv_path}: {error}", file=sys.stderr)
        return 1

    if not records:
        print("Error: no valid records found in the CSV.", file=sys.stderr)
        return 1

    devices = aggregate(records)
    kept, excluded = filter_by_avg_temp(devices, args.max_avg_temp)

    try:
        save_json(args.output, kept, excluded, skipped, args.max_avg_temp)
    except OSError as error:
        print(f"Error: could not write {args.output}: {error}", file=sys.stderr)
        return 1

    print_table(kept)
    print()
    print(f"Devices kept: {len(kept)} | Excluded (avg > {args.max_avg_temp}): {', '.join(excluded) or 'none'}")
    if skipped:
        print(f"Warning: skipped {skipped} invalid row(s).")
    print(f"Saved results to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
