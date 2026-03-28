"""
Contact Information Extractor
Extracts email and phone number for candidate identification
"""

import re


def extract_contact_info(text: str) -> dict:
    """
    Extract contact information from resume

    Args:
        text: Resume text

    Returns:
        {
            "email": "maheshnikas121@gmail.com",
            "phone": "+91 9356736650"
        }
    """
    return {
        "email": extract_email(text),
        "phone": extract_phone(text)
    }


def extract_email(text: str) -> str:
    """
    Extract email address

    Pattern matches:
    - user@domain.com
    - user.name@company.co.in
    - user+tag@domain.org
    """
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(email_pattern, text)

    if matches:
        # Return first email found
        return matches[0]

    return ""


def extract_phone(text: str) -> str:
    """
    Extract phone number (Indian format primarily)

    Matches:
    - +91 9356736650
    - 9356736650
    - +91-9356-7366-50
    - (91) 9356736650
    - 1234567890
    """
    # Pattern for phone numbers
    phone_pattern = r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{3,6}[-\s\.]?[0-9]{4,6}'

    matches = re.findall(phone_pattern, text)

    # Validate: Must have at least 10 digits
    for match in matches:
        digits_only = re.sub(r'\D', '', match)  # Remove non-digits
        if len(digits_only) >= 10:
            return match

    return ""


# Quick test
if __name__ == "__main__":
    test_text = """
    MAHESH S. NIKAS
    Email: maheshnikas121@gmail.com | Phone: +91 9356736650
    """

    contact = extract_contact_info(test_text)
    print(f"Email: {contact['email']}")
    print(f"Phone: {contact['phone']}")