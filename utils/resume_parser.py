import re

def extract_name(text):

    lines = text.split("\n")

    for line in lines:

        line = line.strip()

        if len(line.split()) in [2, 3]:

            if all(word.isalpha() for word in line.split()):

                return line

    return "Not Found"

def extract_email(text):

    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    match = re.search(pattern, text)

    return match.group() if match else "Not Found"


def extract_phone(text):

    pattern = r"(\+91[-\s]?)?[6-9]\d{9}"

    match = re.search(pattern, text)

    return match.group() if match else "Not Found"


def extract_education(text):

    education_keywords = [

        "B.Tech",
        "BTech",
        "Bachelor of Technology",
        "B.E",
        "BE",
        "Bachelor of Engineering",
        "BCA",
        "MCA",
        "B.Sc",
        "M.Sc",
        "M.Tech",
        "Diploma",
        "Intermediate",
        "HSC",
        "SSC"

    ]

    text_lower = text.lower()

    for education in education_keywords:

        if education.lower() in text_lower:
            return education

    return "Not Mentioned"






def extract_experience(text):

    text_lower = text.lower()

    if "fresher" in text_lower:
        return "Fresher"

    experience_pattern = r"(\d+)\+?\s*(years|year|yrs|yr)"

    if re.search(experience_pattern, text_lower):
        return "Experienced"

    if "experience" in text_lower:
        return "Experienced"

    return "No Experience Mentioned"