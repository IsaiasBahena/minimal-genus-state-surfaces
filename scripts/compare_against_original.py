"""
Compare the current package outputs against original computed state-code CSVs.

The script exits immediately on the first mismatch.
"""

import ast
import csv
from pathlib import Path

from tqdm import tqdm
from state_surfaces import run_pipeline


REFERENCE_CSV_FILES = [
    "data/knots/knots_3-12_state_codes.csv",
    "data/knots/knots_13_state_codes.csv",
    "data/knots/knots_14_state_codes.csv",
    "data/knots/knots_15_state_codes.csv",
    "data/knots/knots_16_state_codes.csv",
    "data/knots/knots_17_state_codes.csv",
    "data/knots/knots_18_state_codes.part1.csv",
    "data/knots/knots_18_state_codes.part2.csv",
    "data/links/links_3-11_state_codes.csv",
    "data/links/links_12_state_codes.csv",
    "data/links/links_13_state_codes.csv",
    "data/links/links_14_state_codes.csv",
]


def normalize_state_code(value):
    if isinstance(value, str):
        value = ast.literal_eval(value)
    return [tuple(circle) for circle in value]


def parse_bool(value):
    return str(value).strip().lower() == "true"


def check_csv(csv_path):
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for row in tqdm(rows, desc=f"Checking {csv_path.name}", unit="row"):
        name = row["Name"]
        gauss_code = ast.literal_eval(row["Gauss Code"])

        result = run_pipeline(gauss_code=gauss_code)

        expected_state = normalize_state_code(row["State Code"])
        actual_state = normalize_state_code(result["state_code"])

        expected_genus = int(float(row["Unoriented Genus"]))
        actual_genus = int(result["unoriented_genus"])

        expected_crosscap = int(float(row["Crosscap Number"]))
        actual_crosscap = int(result["crosscap"])

        expected_simple = parse_bool(row["Simple"])
        actual_simple = bool(result["simple"])

        expected_sided = parse_bool(row["2-Sided"])
        actual_sided = bool(result["two_sided"])

        if (
            expected_state != actual_state
            or expected_genus != actual_genus
            or expected_crosscap != actual_crosscap
            or expected_simple != actual_simple
            or expected_sided != actual_sided
        ):
            print("\nMismatch found!\n")

            print(f"CSV: {csv_path}")
            print(f"Name: {name}\n")

            print(f"Expected State Code: {expected_state}")
            print(f"Actual State Code:   {actual_state}\n")

            print(f"Expected Genus: {expected_genus}")
            print(f"Actual Genus:   {actual_genus}\n")

            print(f"Expected Crosscap: {expected_crosscap}")
            print(f"Actual Crosscap:   {actual_crosscap}\n")

            print(f"Expected Simple: {expected_simple}")
            print(f"Actual Simple:   {actual_simple}\n")

            print(f"Expected 2-Sided: {expected_sided}")
            print(f"Actual 2-Sided:   {actual_sided}")

            raise SystemExit(1)

    return len(rows)


def main():
    total_rows = 0

    for csv_file in REFERENCE_CSV_FILES:
        total_rows += check_csv(csv_file)

    print("\nSummary")
    print(f"CSV files checked: {len(REFERENCE_CSV_FILES)}")
    print(f"Rows checked: {total_rows}")
    print("Mismatches: 0")


if __name__ == "__main__":
    main()