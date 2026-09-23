# GPX to CSV: A Beginner-Friendly Python Tutorial

This project teaches how to turn a GPS track (`.gpx`) into a CSV table using Python's standard library. It extracts track points, calculates distance and elevation gain, and creates a file that can be opened in Excel or Google Sheets.

## What the notebook does

1. Reads a GPX file with `xml.etree.ElementTree` and extracts latitude, longitude, elevation, and time from each track point.
2. Uses the Haversine formula to calculate distance between consecutive points, then sums distance and positive elevation changes.
3. Writes one CSV row per track point, including segment and cumulative distance and elevation gain.

## Run the project

Open `Project code notebook.ipynb` in Jupyter. Place a GPX track named `001-multiuse-all-uses (1).gpx` in the same folder, or change `gpx_file` in the notebook to your own GPX file path. Run the cells from top to bottom. The final code cell writes `trail_output_Final_demo.csv` to the working folder.

The parser and CSV export use only Python's standard library. Jupyter is needed to run the notebook interactively. `Final Peoject showcase.html` is a static showcase that you can open in a browser without running Python.

## Motivation

GPX files store useful GPS data in nested XML tags, but that structure is harder for beginners to inspect and analyze than a spreadsheet. This tutorial uses a mountain bike trail as a practical example of turning a specialized file format into a familiar table. It is designed for readers who know basic Python concepts such as loops, functions, lists, and dictionaries but are new to GPX and XML.

## How it works

The notebook first detects whether the GPX file uses an XML namespace, then finds its track points and collects their coordinates, elevation, and time. It uses the Haversine formula to estimate surface distance between each pair of consecutive coordinates. Positive elevation differences count toward total elevation gain; missing elevation values are skipped for that calculation.

The output CSV includes `lat`, `lon`, `ele`, `time`, `seg_dist_m`, `cum_dist_m`, `seg_gain_m`, and `cum_gain_m`, plus a point index. The notebook also prints total distance, total elevation gain, and a percentage calculated as **total elevation gain / total distance × 100**. This percentage describes overall climbing relative to route length; it is not the signed average slope of every segment.

## Limitations and future improvements

- **GPS and elevation noise:** Small measurement errors can inflate distance and elevation gain. Filtering implausible points and smoothing elevation would improve estimates.
- **Different GPX structures:** The parser reads track points (`trkpt`). It could be extended to handle routes and waypoints, as well as multiple track segments separately.
- **Input validation:** Malformed coordinates or elevation values can interrupt processing. Clear validation and error messages would make the tutorial more robust.
- **Grade calculation:** Calculate grade for individual segments and distinguish climbing-only metrics from an average signed slope.
