# certification_extractor.py

def extract_certifications(cert_lines: list[str]) -> dict:
    """
    Classifies certifications into levels.
    NLP only extracts facts, NOT final score.
    """

    certs = {
        "high": 0,
        "middle": 0,
        "low": 0
    }

    for line in cert_lines:
        l = line.lower()

        # High-level institutions
        if any(k in l for k in [
            "aws", "google", "microsoft", "oracle",
            "ibm", "iit", "stanford", "mit"
        ]):
            certs["high"] += 1

        # Middle-level platforms
        elif any(k in l for k in [
            "coursera", "udemy", "edx", "pluralsight"
        ]):
            certs["middle"] += 1

        # Everything else (internship, participation)
        else:
            certs["low"] += 1

    return certs
