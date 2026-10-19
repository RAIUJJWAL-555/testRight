"""Section 3: bar chart of average temperature per device.

Usage:
    python plot_temperatures.py output/summary.json -o output/avg_temperature.png
"""

import argparse
import json
import os
import sys

import matplotlib

matplotlib.use("Agg")  # no display needed, works on servers/CI
import matplotlib.pyplot as plt


def load_devices(json_path):
    with open(json_path, encoding="utf-8") as json_file:
        data = json.load(json_file)
    devices = data.get("devices", [])
    if not devices:
        raise ValueError("No devices found in the JSON file.")
    return devices, data.get("max_average_temperature")


def build_chart(devices, threshold, output_path):
    names = [d["device_id"] for d in devices]
    averages = [d["average_temperature"] for d in devices]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    bars = ax.bar(names, averages, color="#3b7dd8", edgecolor="black", linewidth=0.6)

    ax.bar_label(bars, fmt="%.1f", padding=3)  # value on top of each bar
    if threshold is not None:
        ax.axhline(threshold, color="red", linestyle="--", linewidth=1, label=f"Threshold ({threshold:.0f}°C)")
        ax.legend(loc="upper right")

    ax.set_title("Average Temperature per Device", fontsize=14, fontweight="bold")
    ax.set_xlabel("Device ID")
    ax.set_ylabel("Average Temperature (°C)")
    ax.set_ylim(0, max(max(averages), threshold or 0) * 1.15)
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    ax.set_axisbelow(True)

    fig.tight_layout()  # stops labels/titles from being cut off or overlapping

    folder = os.path.dirname(output_path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Plot average temperature per device from the summary JSON.")
    parser.add_argument("json_path", help="Path to summary JSON created by summarizer.py")
    parser.add_argument("-o", "--output", default="output/avg_temperature.png", help="Output PNG path")
    args = parser.parse_args(argv)

    try:
        devices, threshold = load_devices(args.json_path)
        build_chart(devices, threshold, args.output)
    except FileNotFoundError:
        print(f"Error: file not found: {args.json_path}", file=sys.stderr)
        return 1
    except (ValueError, KeyError, json.JSONDecodeError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Saved chart to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
