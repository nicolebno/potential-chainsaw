import pandas as pd
import pdfplumber
import json
import streamlit as st

# Constants for styling (consider moving to config.json for consistency)
HEADER_FILL = "DDDDDD"
HEADER_FONT_COLOR = "000000"

def extract_benefit_summary_from_pdf(pdf_file):
    """
    Extracts benefit summary information from a PDF file.
    Assumes a specific table structure in the PDF. You'll likely need to adapt this.
    """
    try:
        all_plans = []
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    # This is a very basic approach. You'll need to adapt
                    # based on the actual structure of your PDF.
                    lines = text.split('\n')
                    headers = [h.strip() for h in lines[0].split()] # Assuming first line is headers
                    for line in lines[1:]:
                        values = [v.strip() for v in line.split()]
                        if len(headers) == len(values):
                            plan_data = dict(zip(headers, values))
                            if 'Plan' in plan_data:
                                all_plans.append(plan_data)
        return all_plans
    except Exception as e:
        st.error(f"Error extracting benefit summary from PDF: {e}")
        return None

def build_benefit_summary_dataframe(pdf_file):
    """
    Builds a benefit summary DataFrame from a PDF file.
    """
    benefit_data = extract_benefit_summary_from_pdf(pdf_file)
    if benefit_data:
        return pd.DataFrame(benefit_data)
    return pd.DataFrame()

if __name__ == "__main__":
    st.title("Benefit Summary Builder")
    pdf_file = st.file_uploader("Upload Benefit Summary PDF", type=["pdf"])

    if pdf_file:
        benefit_df = build_benefit_summary_dataframe(pdf_file)
        if not benefit_df.empty:
            st.write("Extracted Benefit Summary:")
            st.dataframe(benefit_df)
            # You might want to save this to JSON or use it directly
            # for the workbook generation.
            benefit_json = benefit_df.to_json(orient='records', indent=2)
            st.download_button("Download Benefit Summary (JSON)", benefit_json, file_name="benefit_summary.json", mime="application/json")
        else:
            st.warning("Could not extract benefit summary or the PDF was empty.")