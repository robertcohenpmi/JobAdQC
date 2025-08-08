# delete.py
import os

def delete_json_files():
    json_files = [
        "job_adverts.json",
        "job_adverts_cleaned.json",
        "job_adverts_details.json",
        "job_adverts_issues.json"
    ]
    for file in json_files:
        if os.path.exists(file):
            os.remove(file)
