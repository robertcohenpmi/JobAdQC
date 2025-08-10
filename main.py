import streamlit as st
from fetch import fetch_job_data
from clean import clean_html
from detect import detect_language
from quality import run_quality_checks
import json
import os
import pandas as pd
from bs4 import BeautifulSoup
from delete import delete_json_files

# Clear previous JSON files
delete_json_files()

# Page setup

st.set_page_config(
    page_title="Job Advert QC Checker",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

with open("branding_styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Sidebar: Minimal info only
with st.sidebar:
    st.image("logo.svg", width=300)
    st.markdown("""
# ℹ️ About this tool
## 🔍 What does this tool do?
- Performs real-time quality checks on currently published job adverts via a direct connection to our external careers site.
- Checks can include:
  - length of advert (default)
  - Non inclusive or discriminatory language (default)
  - Tobacco and smoking terms (default)
  - Language identification
  - Punctuation issues
  - Missing critical fields
  
## ⚠️ Limitations:
- Only checks the Global Careers page.

Version 1.0 Prod

## Created By [Rob Cohen](https://engage.cloud.microsoft/main/users/eyJfdHlwZSI6IlVzZXIiLCJpZCI6IjE0MTA0OTYxODQzMiJ9/storyline)
""")

# Main layout: Two columns
col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown("### Select Quality Checks")

    # Select All toggle
    select_all = st.toggle("Select All Checks", value=False)

    # Compact layout using columns
    c1, c2 = st.columns(2)

    with c1:
        check_short_description = st.checkbox("Short description", value=select_all or True)
        check_non_inclusive = st.checkbox("Non-inclusive language", value=select_all or True)
        check_discriminatory = st.checkbox("Discriminatory language", value=select_all or True)
        check_tobacco_terms = st.checkbox("Tobacco-related terms", value=select_all or True)


    
    with c2:
        check_language_mismatch = st.checkbox("Language mismatch", value=select_all)
        check_missing_fields = st.checkbox("Missing fields", value=select_all)
        check_punctuation = st.checkbox("Punctuation issues", value=select_all)

    # Build selected_checks list
    selected_checks = []
    if check_missing_fields:
        selected_checks.append("Missing fields")
    if check_short_description:
        selected_checks.append("Short description")
    if check_non_inclusive:
        selected_checks.append("Non-inclusive language")
    if check_tobacco_terms:
        selected_checks.append("Tobacco-related terms")
    if check_language_mismatch:
        selected_checks.append("Language mismatch")
    if check_punctuation:
        selected_checks.append("Punctuation issues")
    if check_discriminatory:
        selected_checks.append("Discriminatory language")

    # Run button
    run_check = st.button("▶️ Run QC Check")

with col2:
    if run_check:
        xml_url = "https://jobboards-ir.phenommarket.com/feeds/pmipmigb-en-gb-feed-generic"
        job_list = fetch_job_data(xml_url)
        if job_list:
            with open("job_adverts.json", "w", encoding="utf-8") as f:
                json.dump(job_list, f, ensure_ascii=False, indent=4)
            st.success(f"✅ Found {len(job_list)} currently published job adverts.")

            progress = st.progress(0, text="🧼 Cleaning HTML...")
            for i, job in enumerate(job_list):
                job["description_html"] = clean_html(job["description_html"])
                progress.progress((i + 1) / len(job_list), text=f"🧼 Cleaning HTML... ({i + 1}/{len(job_list)})")
            progress.empty()

            with open("job_adverts_cleaned.json", "w", encoding="utf-8") as f:
                json.dump(job_list, f, ensure_ascii=False, indent=4)
            st.success("✅ Cleaned HTML.")

            language_details = []
            quality_issues = []
            progress = st.progress(0, text="🔍 Detecting language and checking quality...")
            for i, job in enumerate(job_list):
                plain_text = BeautifulSoup(job["description_html"], "html.parser").get_text()
                lang_code = detect_language(plain_text)
                language_details.append({
                    "reference_number": job.get("reference_number", ""),
                    "determined_language": lang_code
                })
                issues = run_quality_checks(job, lang_code, selected_checks)
                quality_issues.append({
                    "reference_number": job.get("reference_number", ""),
                    "title": job.get("title", ""),
                    "country": job.get("country", ""),
                    "determined_language": lang_code,
                    "issues": issues
                })
                progress.progress((i + 1) / len(job_list), text=f"🔍 Processing... ({i + 1}/{len(job_list)})")
            progress.empty()

            with open("job_adverts_details.json", "w", encoding="utf-8") as f:
                json.dump(language_details, f, ensure_ascii=False, indent=4)
            st.success("✅ Language detection complete.")

            with open("job_adverts_issues.json", "w", encoding="utf-8") as f:
                json.dump(quality_issues, f, ensure_ascii=False, indent=4)
            st.success("✅ Quality checks complete.")

# Results section
st.markdown("### 🚨 Job Quality Issues")
if os.path.exists("job_adverts_issues.json"):
    with open("job_adverts_issues.json", "r", encoding="utf-8") as f:
        issues_data = json.load(f)
    issues_summary = []
    issue_counts = {}
    for entry in issues_data:
        if entry["issues"]:
            ref = entry["reference_number"]
            issues_summary.append({
                "Reference": f"https://join.pmicareers.com/gb/en/job/{ref}",
                "Title": entry["title"],
                "Country": entry["country"],
                "Language": entry["determined_language"],
                "Issues": "; ".join(entry["issues"])
            })
            for issue in entry["issues"]:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
    if issues_summary:
        df_issues = pd.DataFrame(issues_summary)
        st.dataframe(df_issues, use_container_width=True, hide_index=True)
        st.markdown("### 🧾 Job Quality Issues Summary Table")
        st.markdown(f"**Total Issues Found:** {sum(issue_counts.values())}")
        df_summary = pd.DataFrame(list(issue_counts.items()), columns=["Issue Type", "Count"])
        df_summary = df_summary.sort_values("Count", ascending=False)
        st.dataframe(df_summary, use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ No issues found.")
else:
    st.info("ℹ️ Please run QC Check for results.")















