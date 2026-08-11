import re

# You can expand this list over time
SKILLS = [
    "python",
    "java",
    "c",
    "c++",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "flask",
    "django",
    "fastapi",
    "html",
    "css",
    "javascript",
    "react",
    "node",
    "git",
    "github",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "linux",
    "machine learning",
    "deep learning",
    "nlp",
    "tensorflow",
    "pytorch",
    "pandas",
    "numpy",
    "scikit-learn",
    "rest api"
]

def extract_skills(text):
    text = text.lower()

    found = []

    for skill in SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text):
            found.append(skill)

    return sorted(list(set(found)))