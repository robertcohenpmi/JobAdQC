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
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            min-width: 450px;
            max-width: 450px;
        }
    </style>
    """, unsafe_allow_html=True)

st.title("🌐 External Careers Job Adverts – Quality Checker")

# Sidebar: Controls & Logs
with st.sidebar:
    st.subheader("⚙️ Running the QC Tool")
    st.markdown("""
**🔍 What does this tool do?**
- Performs real-time quality checks on job adverts via a direct connection to Phenom.
- Checks include:
  - Missing fields
  - Short descriptions
  - Non-inclusive language
  - Language mismatches
  - Smoking terms

**⚠️ Current Limitations:**
- Only checks the English External Careers page.
""")
    if st.button("▶️ Run QC Check"):
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
            st.success("✅ Language detection complete.")

            with open("job_adverts_issues.json", "w", encoding="utf-8") as f:
                json.dump(quality_issues, f, ensure_ascii=False, indent=4)
            st.success("✅ Quality checks complete.")
    st.markdown("""
**📙 About**

This is a protoytpye tool which was created by Rob Cohen
""")
# Main column: Job Quality Issues
st.subheader("🚨 Job Quality Issues")
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
        st.markdown(f"**Total Issues Found:** {sum(issue_counts.values())}")  # 👈 New line added here
        df_summary = pd.DataFrame(list(issue_counts.items()), columns=["Issue Type", "Count"])
        df_summary = df_summary.sort_values("Count", ascending=False)
        st.dataframe(df_summary, use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ No issues found.")
else:
    st.info("ℹ️ Please run QC Check for results.")






