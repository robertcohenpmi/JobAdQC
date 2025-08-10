from bs4 import BeautifulSoup

def run_quality_checks(job, detected_language, selected_checks):
    issues = []

    plain_text = BeautifulSoup(job.get("description_html", ""), "html.parser").get_text()

    if "Missing fields" in selected_checks:
        required_fields = ["title", "description_html", "reference_number", "country", "city"]
        for field in required_fields:
            if not job.get(field):
                issues.append(f"Missing or empty field: {field}")

    if "Short description" in selected_checks:
        if len(plain_text) < 500:
            issues.append("Description too short (<500 characters)")

    if "Non-inclusive language" in selected_checks:
        gendered_terms = [
            " he ", " she ", " his ", " her ", "he/she", "his/her", "him/her",
            "chairman", "manpower", "woman", " male ", " female "
        ]
        for term in gendered_terms:
            if term.lower() in plain_text.lower():
                issues.append(f"Non-inclusive language: '{term}' found")

    if "Tobacco-related terms" in selected_checks:
        tobacco_terms = [" cigarette ", " malboro ", " smoking ", " vape ", " cancer "]
        for term in tobacco_terms:
            if term.lower() in plain_text.lower():
                issues.append(f"Tobacco-related term: '{term}' found")

    if "Language mismatch" in selected_checks:
        expected_language = "en" if job.get("country", "").lower() in ["united kingdom", "usa", "canada", "australia"] else None
        if expected_language and detected_language != expected_language:
            issues.append(f"Language mismatch: expected {expected_language}, got {detected_language}")

    if "Punctuation issues" in selected_checks:
        if plain_text.count("!") > 3:
            issues.append("Excessive use of exclamation marks")
        if not any(p in plain_text for p in ".!?"):
            issues.append("Lack of punctuation in description")

    if "Discriminatory language" in selected_checks:
        discriminatory_terms = [
            " young ", " recent graduate ", " native ", " energetic ", " youthful ",
            " mature ", " old ", " aged ", " perfect ", " able-bodied ", " healthy ",
            " attractive ", " well-groomed ", " presentable ", " good looking ",
            " unmarried ", " aggressive ", " dominant ", " rockstar ", " guru ",
            " ninja ", " fast-paced ", " high energy"
        ]
        for term in discriminatory_terms:
            if term.lower() in plain_text.lower():
                issues.append(f"Potentially discriminatory language: '{term}' found")

    return issues
