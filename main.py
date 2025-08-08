# Entry point for the Streamlit app
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

delete_json_files()

st.set_page_config(layout="wide")
st.title("🌐 PMI External Careers Job Adverts – Quality Checker")

view_option = st.sidebar.radio("📊 Explore Job Data", ["None", "Jobs per Country", "Jobs per Language"])
col1, col3 = st.columns([1, 1])

with col1:
    st.subheader("⚙️ Controls & Logs")
    st.markdown("""
**🔍 What does this tool do?**
- Performs real-time quality checks on job adverts via a direct connection to Phenom.
- Checks include:
  - Missing fields
  - Short descriptions
  - Non-inclusive language
  - Language mismatches
  
**⚠️ Current Limitations:**
- Only checks the English External Careers page.
""")
    if st.button("▶️ Run QC Check"):
        xml_url = "https://jobboards-ir.phenommarket.com/feeds/pmipmigb-en-gb-feed-generic"
        job_list = fetch_job_data(xml_url)
        if job_list:
            with open("job_adverts.json", "w", encoding="utf-8") as f:
                json.dump(job_list, f, ensure_ascii=False, indent=4)
            st.success(f"✅ Saved {len(job_list)} job entries to job_adverts.json.")

            progress = st.progress(0, text="🧼 Cleaning HTML...")
            for i, job in enumerate(job_list):
                job["description_html"] = clean_html(job["description_html"])
                progress.progress((i + 1) / len(job_list), text=f"🧼 Cleaning HTML... ({i + 1}/{len(job_list)})")
            progress.empty()

            with open("job_adverts_cleaned.json", "w", encoding="utf-8") as f:
                json.dump(job_list, f, ensure_ascii=False, indent=4)
            st.success("✅ Cleaned HTML and saved to job_adverts_cleaned.json.")

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
                issues = run_quality_checks(job, lang_code)
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
            st.success("✅ Language detection complete. Saved to job_adverts_details.json.")

            with open("job_adverts_issues.json", "w", encoding="utf-8") as f:
                json.dump(quality_issues, f, ensure_ascii=False, indent=4)
            st.success("✅ Quality checks complete. Saved to job_adverts_issues.json.")

if view_option == "Jobs per Country":
    st.subheader("🌍 Jobs per Country")
    if os.path.exists("job_adverts_cleaned.json"):
        with open("job_adverts_cleaned.json", "r", encoding="utf-8") as f:
            job_list = json.load(f)
        country_counts = {}
        for job in job_list:
            country = job.get("country", "Unknown")
            country_counts[country] = country_counts.get(country, 0) + 1
        df_country = pd.DataFrame(list(country_counts.items()), columns=["Country", "Job Count"])
        df_country = df_country.sort_values("Job Count", ascending=False)
        st.dataframe(df_country, use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ No cleaned job data available. Please run the QC check first.")

elif view_option == "Jobs per Language":
    st.subheader("🌐 Jobs per Language")
    if os.path.exists("job_adverts_details.json"):
        with open("job_adverts_details.json", "r", encoding="utf-8") as f:
            lang_data = json.load(f)
        lang_counts = {}
        for entry in lang_data:
            lang = entry.get("determined_language", "unknown")
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
        df_lang = pd.DataFrame(list(lang_counts.items()), columns=["Language", "Job Count"])
        df_lang = df_lang.sort_values("Job Count", ascending=False)
        st.dataframe(df_lang, use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ No language data available. Please run the QC check first.")

with col3:
    st.subheader("🚨 Job Quality Issues")
    if os.path.exists("job_adverts_issues.json"):
        with open("job_adverts_issues.json", "r", encoding="utf-8") as f:
            issues_data = json.load(f)
        issues_summary = []
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
        if issues_summary:
            df_issues = pd.DataFrame(issues_summary)
            st.dataframe(df_issues, use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ No issues found.")
    else:
        st.info("ℹ️ No issues found or file missing.")
