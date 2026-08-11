import os
import csv

from flask import (
    Flask,
    render_template,
    request,
    send_file
)

from werkzeug.utils import secure_filename

from utils.pdf_reader import extract_pdf_text
from utils.docx_reader import extract_docx_text
from utils.txt_reader import extract_txt_text

from models.resume_matcher import rank_resumes

app = Flask(__name__)

app.secret_key = "resume_screening_project"

UPLOAD_FOLDER = "uploads"
RESUME_FOLDER = os.path.join(UPLOAD_FOLDER, "resumes")
JOB_FOLDER = os.path.join(UPLOAD_FOLDER, "job_descriptions")

app.config["RESUME_FOLDER"] = RESUME_FOLDER
app.config["JOB_FOLDER"] = JOB_FOLDER

os.makedirs(RESUME_FOLDER, exist_ok=True)
os.makedirs(JOB_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

latest_results = []


def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def extract_text(filepath):

    if filepath.lower().endswith(".pdf"):
        return extract_pdf_text(filepath)

    elif filepath.lower().endswith(".docx"):
        return extract_docx_text(filepath)

    elif filepath.lower().endswith(".txt"):
        return extract_txt_text(filepath)

    return ""


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    global latest_results

    resumes = request.files.getlist("resumes")
    job_description = request.files.get("job_description")

    if len(resumes) == 0:
        return "Please upload at least one resume."

    if not job_description:
        return "Please upload Job Description."

    resume_texts = []

    for resume in resumes:

        if resume and allowed_file(resume.filename):

            filename = secure_filename(resume.filename)

            filepath = os.path.join(
                app.config["RESUME_FOLDER"],
                filename
            )

            resume.save(filepath)

            text = extract_text(filepath)

            resume_texts.append({

                "filename": filename,

                "text": text

            })

    jd_filename = secure_filename(job_description.filename)

    jd_path = os.path.join(
        app.config["JOB_FOLDER"],
        jd_filename
    )

    job_description.save(jd_path)

    job_text = extract_text(jd_path)

    ranked_candidates = rank_resumes(
        job_text,
        resume_texts
    )

    latest_results = ranked_candidates

    if len(ranked_candidates) == 0:
        return "No valid resumes found."

    total_resumes = len(ranked_candidates)

    highest_score = max(
        candidate["ats_score"]
        for candidate in ranked_candidates
    )

    average_score = round(
        sum(
            candidate["ats_score"]
            for candidate in ranked_candidates
        ) / total_resumes,
        2
    )

    best_candidate = ranked_candidates[0]["filename"]

    recommended_count = len([
        candidate
        for candidate in ranked_candidates
        if candidate["recommendation"] in
        ["Highly Recommended", "Recommended"]
    ])

    return render_template(

        "results.html",

        ranked_candidates=ranked_candidates,

        total_resumes=total_resumes,

        highest_score=highest_score,

        average_score=average_score,

        best_candidate=best_candidate,

        recommended_count=recommended_count

    )


@app.route("/download")
def download():

    global latest_results

    filename = "resume_ranking.csv"

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow([

            "Rank",

            "Resume",

            "ATS Score",

            "AI Score",

            "Skill Match",

            "Resume Level",

            "Interview Chance",

            "Recommendation",

            "Email",

            "Phone",

            "Education",

            "Experience"

        ])

        rank = 1

        for candidate in latest_results:

            writer.writerow([

                rank,

                candidate["filename"],

                candidate["ats_score"],

                candidate["score"],

                candidate["skill_match_percentage"],

                candidate["resume_level"],

                candidate["interview_chance"],

                candidate["recommendation"],

                candidate["email"],

                candidate["phone"],

                candidate["education"],

                candidate["experience"]

            ])

            rank += 1

    return send_file(
        filename,
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True)