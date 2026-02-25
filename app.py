from flask import Flask, render_template,request
import PyPDF2

from flask import send_file
import io

app = Flask(__name__)

SKILLS = [

# Programming Languages
"python", "java", "c", "c++", "c#", "javascript", "typescript", "go", "rust", "kotlin",

# Web Development
"html", "css", "react", "angular", "vue", "node.js", "express", "flask", "django", "spring",

# Databases
"sql", "mysql", "postgresql", "mongodb", "sqlite", "oracle", "firebase",

# Data Science / ML
"machine learning", "deep learning", "pandas", "numpy", "matplotlib", "seaborn",
"scikit-learn", "tensorflow", "keras", "opencv",

# Tools
"git", "github", "docker", "kubernetes", "jenkins", "linux", "bash",

# Cloud
"aws", "azure", "gcp",

# Core CS
"data structures", "algorithms", "oop", "operating systems",
"computer networks", "dbms",

# Others
"rest api", "api", "json", "xml", "unit testing", "debugging"
]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    resume_file=request.files["resume"]
    job_desc=request.form["job_desc"]
    
    pdf_reader=PyPDF2.PdfReader(resume_file)
    resume_text=""

    for page in pdf_reader.pages:
        resume_text+=page.extract_text()

    import re

    resume_text = resume_text.lower()
    resume_words = set(re.findall(r'\b\w+\b', resume_text))

    resume_skills=set()
    job_skills=set()

    job_words = set(re.findall(r'\b\w+\b', job_desc.lower()))

    for skill in SKILLS:
        skill_words = skill.split()

        if all(word in resume_words for word in skill_words):
            resume_skills.add(skill)

        if all(word in job_words for word in skill_words):
            job_skills.add(skill)

    matched_skills = resume_skills.intersection(job_skills)
    missing_skills= job_skills - matched_skills
    recommended_skills = list(missing_skills)



    if len(job_skills)==0:
        match_percentage=0
    else:
        match_percentage = (len(matched_skills) / len(job_skills)) * 100

    global last_result

    last_result={
        "match_percentage": round(match_percentage, 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "recommended_skills": recommended_skills
    }

    return render_template(
        "result.html",
        match_percentage=round(match_percentage, 2),
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        recommended_skills=recommended_skills

    )

@app.route("/download_report")
def download_report():

    report=f"""
    Resume Analysis Report

    Match Percentage: {last_result['match_percentage']}%
    Matched Skills:
    {chr(10).join(last_result['matched_skills'])}

    Missing Skills:
    {chr(10).join(last_result['missing_skills'])}
  
    Recommended Skills:
    {chr(10).join(last_result['recommended_skills'])}
    """

    buffer=io.BytesIO()
    buffer.write(report.encode("utf-8"))
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="resume_analysis_report.txt",
        mimetype="text/plain"
    )

    
if __name__=="__main__":
    app.run(debug=True)

    