from bs4 import BeautifulSoup

def run_quality_checks(job, detected_language):
    issues = []
    required_fields = ["title", "description_html", "reference_number", "country", "city"]
    for field in required_fields:
        if not job.get(field):
            issues.append(f"Missing or empty field: {field}")
    plain_text = BeautifulSoup(job.get("description_html", ""), "html.parser").get_text()
    if len(plain_text) < 500:
        issues.append("Description too short (<500 characters)")
    gendered_terms = ["he/she", "his/her", "him/her", "chairman", "manpower"]
    for term in gendered_terms:
        if term.lower() in plain_text.lower():
            issues.append(f"Non-inclusive language: '{term}' found")
    expected_language = "en" if job.get("country", "").lower() in ["united kingdom", "usa", "canada", "australia"] else None
    if expected_language and detected_language != expected_language:
        issues.append(f"Language mismatch: expected {expected_language}, got {detected_language}")
    return issues
