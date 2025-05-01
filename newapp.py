import json
import sys
import pandas as pd
from datetime import datetime
from openpyxl import Workbook
from build_benefit_summary import build_benefit_summary

# --- Load Config ---
with open("config.json", "r") as f:
    config = json.load(f)

BRAND = config["branding"]
FORMATS = config["formats"]

# --- Style Settings ---
PRIMARY_COLOR = BRAND["primary_color"].replace("#", "")
FONT_NAME = BRAND["font"]
CURRENCY_FORMAT = FORMATS["currency"]
DATE_FORMAT = FORMATS["date"]

# --- Contribution Settings from CLI ---
contrib_type = sys.argv[1] if len(sys.argv) > 1 else "flat"
contrib_employee = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
contrib_dependent = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0

# --- Optional Plan Data from JSON file ---
try:
    with open("plans.json", "r") as f:
        plan_data = json.load(f)
except FileNotFoundError:
    plan_data = []

# --- Load Data ---
census_df = pd.read_excel("uploaded_census.xlsx")
rate_df = pd.read_excel("uploaded_rates.xlsx", header=0)
renewal_df = pd.read_excel("uploaded_renewal_rates.xlsx", header=0)

# --- Basic Age Calculation ---
renewal_date = datetime(2025, 5, 1)
census_df['DOB'] = pd.to_datetime(census_df['DOB'], errors='coerce')
census_df['Age at Renewal'] = census_df['DOB'].apply(
    lambda dob: renewal_date.year - dob.year - ((renewal_date.month, renewal_date.day) < (dob.month, dob.day))
    if pd.notnull(dob) else None
)

# --- Workbook Setup ---
wb = Workbook()
ws = wb.active
ws.title = "Financial Summary"

# Placeholder summary row
ws.append(["Plan", "Monthly Premium", "Employer Share", "Employee Share"])
ws.append(["Sample Plan", 1200, 900, 300])

# --- Benefit Summary Tab ---
benefit_ws = wb.create_sheet(title="Benefit Summary")
build_benefit_summary(benefit_ws, plan_data)

# --- Save Workbook ---
wb.save("financial_summary_output.xlsx")
