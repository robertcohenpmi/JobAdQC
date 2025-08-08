import requests
import xml.etree.ElementTree as ET
from html import unescape
import streamlit as st

def fetch_job_data(xml_url):
    try:
        response = requests.get(xml_url)
        response.raise_for_status()
        xml_content = response.content
        root = ET.fromstring(xml_content)
        jobs = []
        all_jobs = root.findall(".//job")
        progress = st.progress(0, text="📥 Downloading jobs...")
        for i, job in enumerate(all_jobs):
            job_data = {
                "title": job.findtext("title", default="").strip(),
                "date": job.findtext("date", default="").strip(),
                "reference_number": job.findtext("referencenumber", default="").strip(),
                "url": job.findtext("url", default="").strip(),
                "city": job.findtext("city", default="").strip(),
                "country": job.findtext("country", default="").strip(),
                "description_html": unescape(job.findtext("description", default="").strip())
            }
            jobs.append(job_data)
            progress.progress((i + 1) / len(all_jobs), text=f"📥 Downloading jobs... ({i + 1}/{len(all_jobs)})")
        progress.empty()
        return jobs
    except Exception as e:
        st.error(f"❌ Failed to fetch job data: {e}")
        return []
