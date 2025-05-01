import streamlit as st
import pandas as pd
import json
from generate_workbook import generate_excel_workbook
from build_benefit_summary import build_benefit_summary_dataframe
import os
import subprocess

st.title("Insurance Proposal Workbook Generator")

census_file = st.file_uploader("Upload Census Data (Excel)", type=["xlsx"])
rates_file = st.file_uploader("Upload Rates Data (Excel)", type=["xlsx"])
benefit_summary_pdf = st.file_uploader("Upload Benefit Summary (PDF)", type=["pdf"])

st.subheader("OR Enter Benefit Summary as JSON")
benefit_summary_text = st.text_area("Benefit Summary (JSON)", '[\n  {"Plan": "Plan A"}, \n  {"Plan": "Plan B"}\n]')

benefit_summary_data = []
if benefit_summary_pdf:
    benefit_df = build_benefit_summary_dataframe(benefit_summary_pdf)
    if not benefit_df.empty:
        benefit_summary_data = benefit_df.to_dict(orient='records')
    else:
        st.warning("Could not extract benefit summary from PDF.")
elif benefit_summary_text:
    try:
        benefit_summary_data = json.loads(benefit_summary_text)
        if not isinstance(benefit_summary_data, list):
            st.error("Benefit Summary must be a JSON list of dictionaries.")
            benefit_summary_data = []
    except json.JSONDecodeError:
        st.error("Invalid JSON format for Benefit Summary.")
        benefit_summary_data = []

if census_file and rates_file and benefit_summary_data:
    if st.button("Generate Workbook"):
        with st.spinner("Generating Excel Workbook..."):
            workbook = generate_excel_workbook(census_file, rates_file, benefit_summary_data)
            if workbook:
                try:
                    # Save the workbook to a BytesIO object for download
                    from io import BytesIO
                    buffer = BytesIO()
                    workbook.save(buffer)
                    buffer.seek(0)

                    st.download_button(
                        label="Download Excel Workbook",
                        data=buffer,
                        file_name="financial_proposal_workbook.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    st.success("Workbook generated and ready for download!")
                except Exception as e:
                    st.error(f"Error during download: {e}")

# Example of running a subprocess (as seen in your logs)
st.subheader("Run Subprocess (Example - Adapt as needed)")
command_to_run = st.text_input("Enter command to run:", "")
if st.button("Run Command"):
    if command_to_run:
        try:
            result = subprocess.run(command_to_run, shell=True, capture_output=True, text=True, check=True)
            st.success(f"Command executed successfully:\n{result.stdout}")
            if result.stderr:
                st.warning(f"Command had errors/warnings:\n{result.stderr}")
        except subprocess.CalledProcessError as e:
            st.error(f"Error executing command: {e}")
        except FileNotFoundError:
            st.error(f"Command not found: {command_to_run}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")