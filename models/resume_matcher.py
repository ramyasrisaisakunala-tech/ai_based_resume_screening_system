from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils.skill_matcher import extract_skills
from utils.resume_parser import (
    extract_name,
    extract_email,
    extract_phone,
    extract_education,
    extract_experience
)


def rank_resumes(job_description, resume_list):
    if not job_description.strip():
        return []

    job_skills = list(set(extract_skills(job_description)))

    valid_resumes = []

    for resume in resume_list:
        resume_text = resume.get("text", "")

        if resume_text.strip():
            valid_resumes.append(resume)

    if not valid_resumes:
        return []

    documents = [job_description]

    for resume in valid_resumes:
        documents.append(resume["text"])

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=5000
    )

    tfidf_matrix = vectorizer.fit_transform(documents)

    job_vector = tfidf_matrix[0]
    resume_vectors = tfidf_matrix[1:]

    similarities = cosine_similarity(
        job_vector,
        resume_vectors
    )[0]

    ranked_candidates = []

    for index, resume in enumerate(valid_resumes):
        resume_text = resume["text"]

        score = round(similarities[index] * 100, 2)

        resume_skills = list(set(extract_skills(resume_text)))

        matched_skills = sorted(
            list(set(job_skills) & set(resume_skills))
        )

        missing_skills = sorted(
            list(set(job_skills) - set(resume_skills))
        )

        if job_skills:
            skill_match_percentage = round(
                (len(matched_skills) / len(job_skills)) * 100,
                2
            )
        else:
            skill_match_percentage = 0

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
            (score * 0.50)
            + (skill_match_percentage * 0.35)
            + (completeness * 0.15),
            2
        )

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

        strengths = []

        if skill_match_percentage >= 80:
            strengths.append("Strong Skill Match")

        if score >= 85:
            strengths.append("High AI Similarity")

        if extract_email(resume_text) != "Not Found":
            strengths.append("Email Available")

        if extract_phone(resume_text) != "Not Found":
            strengths.append("Phone Available")

        if extract_education(resume_text) != "Not Mentioned":
            strengths.append("Education Mentioned")

        if extract_experience(resume_text) != "No Experience Mentioned":
            strengths.append("Experience Mentioned")

        if not strengths:
            strengths.append("Basic Resume")

        weaknesses = []

        if skill_match_percentage < 60:
            weaknesses.append("Low Skill Match")

        if missing_skills:
            weaknesses.append("Missing Required Skills")

        if extract_email(resume_text) == "Not Found":
            weaknesses.append("Email Missing")

        if extract_phone(resume_text) == "Not Found":
            weaknesses.append("Phone Missing")

        if not weaknesses:
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
