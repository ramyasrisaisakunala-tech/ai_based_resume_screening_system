from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from utils.skill_matcher import extract_skills
from utils.resume_parser import (
    extract_email,
    extract_phone,
    extract_education,
    extract_experience
)
from utils.resume_parser import (
    extract_name,
    extract_email,
    extract_phone,
    extract_education,
    extract_experience
)

# Load AI model only once
model = SentenceTransformer("all-MiniLM-L6-v2")


def rank_resumes(job_description, resume_list):

    # Empty JD
    if not job_description.strip():
        return []

    # Generate embedding for JD
    job_embedding = model.encode(job_description)

    # Extract Job Skills
    job_skills = list(set(extract_skills(job_description)))

    ranked_candidates = []

    for resume in resume_list:

        resume_text = resume["text"]

        if not resume_text.strip():
            continue

        # Resume Embedding
        resume_embedding = model.encode(resume_text)

        similarity = cosine_similarity(
            [job_embedding],
            [resume_embedding]
        )[0][0]

        score = round(similarity * 100, 2)

        # Resume Skills
        resume_skills = list(set(extract_skills(resume_text)))

        matched_skills = sorted(
            list(set(job_skills) & set(resume_skills))
        )

        missing_skills = sorted(
            list(set(job_skills) - set(resume_skills))
        )

        # Skill Match %
        if job_skills:
            skill_match_percentage = round(
                (len(matched_skills) / len(job_skills)) * 100,
                2
            )
        else:
            skill_match_percentage = 0

        # ATS Score
        completeness = 0

        if extract_email(resume_text) != "Not Found":
         completeness += 25

        if extract_phone(resume_text) != "Not Found":
         completeness += 25

        if extract_education(resume_text) != "Not Mentioned":
         completeness += 25

        if extract_experience(resume_text) != "No Experience Mentioned":
         completeness += 25

        ats_score = round(
            (score * 0.50) +
            (skill_match_percentage * 0.35) +
            (completeness * 0.15),
            2
        )

        # Resume Level
        if ats_score >= 90:
            resume_level = "Excellent"
            interview_chance = "95%"
            recommendation = "Highly Recommended"

        elif ats_score >= 80:
            resume_level = "Very Good"
            interview_chance = "85%"
            recommendation = "Recommended"

        elif ats_score >= 70:
            resume_level = "Good"
            interview_chance = "70%"
            recommendation = "Consider"

        elif ats_score >= 60:
            resume_level = "Average"
            interview_chance = "50%"
            recommendation = "Needs Improvement"

        else:
            resume_level = "Poor"
            interview_chance = "25%"
            recommendation = "Not Recommended"

        # Strengths
        strengths = []

        if skill_match_percentage >= 80:
            strengths.append("Strong Skill Match")

        if score >= 85:
            strengths.append("High AI Similarity")

        if extract_email(resume_text) != "Not Found":
            strengths.append("Email Available")

        if extract_phone(resume_text) != "Not Found":
            strengths.append("Phone Available")

        if extract_education(resume_text) != "Not Found":
            strengths.append("Education Mentioned")

        if extract_experience(resume_text) != "Not Found":
            strengths.append("Experience Mentioned")

        if len(strengths) == 0:
            strengths.append("Basic Resume")

        # Weaknesses
        weaknesses = []

        if skill_match_percentage < 60:
            weaknesses.append("Low Skill Match")

        if len(missing_skills) > 0:
            weaknesses.append("Missing Required Skills")

        if extract_email(resume_text) == "Not Found":
            weaknesses.append("Email Missing")

        if extract_phone(resume_text) == "Not Found":
            weaknesses.append("Phone Missing")

        if len(weaknesses) == 0:
            weaknesses.append("No Major Issues")

        ranked_candidates.append({

            "name": extract_name(resume_text),
          
            "filename": resume["filename"],

            "score": score,

            "ats_score": ats_score,

            "skill_match_percentage": skill_match_percentage,

            "recommendation": recommendation,

            "resume_level": resume_level,

            "interview_chance": interview_chance,

            "matched_skills": matched_skills,

            "missing_skills": missing_skills,

            "strengths": strengths,

            "weaknesses": weaknesses,

            "email": extract_email(resume_text),

            "phone": extract_phone(resume_text),

            "education": extract_education(resume_text),

            "experience": extract_experience(resume_text)

        })

    ranked_candidates.sort(
        key=lambda candidate: candidate["ats_score"],
        reverse=True
    )

    return ranked_candidates