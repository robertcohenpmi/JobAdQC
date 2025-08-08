from bs4 import BeautifulSoup

def run_quality_checks(job, detected_language):
    issues = []

    # Check for required fields
    required_fields = ["title", "description_html", "reference_number", "country", "city"]
    for field in required_fields:
        if not job.get(field):
            issues.append(f"Missing or empty field: {field}")

    # Convert HTML description to plain text
    plain_text = BeautifulSoup(job.get("description_html", ""), "html.parser").get_text()

    # Check for short description
    if len(plain_text) < 500:
        issues.append("Description too short (<500 characters)")

    # Check for non-inclusive language
    gendered_terms = [" he ", " she ", " his ", " her ", "he/she", "his/her", "him/her", "chairman", "manpower"]
    for term in gendered_terms:
        if term.lower() in plain_text.lower():
            issues.append(f"Non-inclusive language: '{term}' found")

    # Check for tobacco-related terms
    tobacco_terms = ["cigarette", "malboro", "smoking", "vape", "cancer"]
    for term in tobacco_terms:
        if term.lower() in plain_text.lower():
            issues.append(f"Tobacco-related term: '{term}' found")

    # Check for language mismatch
    expected_language = "en" if job.get("country", "").lower() in ["united kingdom", "usa", "canada", "australia"] else None
    if expected_language and detected_language != expected_language:
        issues.append(f"Language mismatch: expected {expected_language}, got {detected_language}")

    # Check for excessive punctuation    
    if plain_text.count("!") > 3 or any(word.isupper() for word in plain_text.split() if len(word) > 4):
    issues.append("Excessive emphasis (e.g., ALL CAPS or too many exclamation marks)")

    # Check for Job Type
    job_type_keywords = ["full-time", "part-time", "contract", "freelance", "intern", "inkompass"]
        if not any(term in plain_text.lower() for term in job_type_keywords):
            issues.append("Job type not specified")

    # Check for discrimination
    discriminatory_terms = ["young", "energetic", "native english speaker", "able-bodied"]
        for term in discriminatory_terms:
            if term.lower() in plain_text.lower():
                issues.append(f"Potentially discriminatory language: '{term}' found")


    return issues

